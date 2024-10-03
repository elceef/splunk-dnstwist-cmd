#!/usr/bin/env python3

'''
Created by Marcin Ulikowski <marcin@ulikowski.pl>


Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import os, sys
import csv
import time
import re

from itertools import repeat

from multiprocessing import Pool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option
from dnstwist import Fuzzer, Permutation, UrlParser


WORKERS = min((os.cpu_count()//2)+1, 32) # use half of the logical CPU, up to 32


def worker(task):
    domain, fuzzers, dictionary, tld_dictionary = task
    try:
        fuzz = Fuzzer(UrlParser(domain).domain,
                      dictionary=dictionary,
                      tld_dictionary=tld_dictionary)
        fuzz.generate(fuzzers=fuzzers)
    except Exception as err:
        return (domain, err)
    else:
        fuzz.domains.discard(Permutation(fuzzer='*original', domain=domain))
        return (domain, fuzz.permutations())


@Configuration(type='streaming')
class dnstwistCommand(GeneratingCommand):

    csvfile = Option(doc='''
        **Syntax:** **csvfile=***<path>*
        **Description:** CSV lookup file name
        ''', name='csvfile', require=False)

    csvapp = Option(doc='''
        **Syntax:** **csvapp=***<app name>*
        **Description:** Application name that contains the CSV lookup file
        ''', name='csvapp', require=False, default=__file__.split(os.sep)[-3])

    csvcol = Option(doc='''
        **Syntax:** **csvcol=***<column>*
        **Description:** Column name in CSV lookup file (default: domain)
        ''', name='csvcol', require=False, default='domain')

    dictionary = Option(doc='''
        **Syntax:** **dictionary=***<word ...>*
        **Description:** Generate more permutations using dictionary words
        ''', name='dictionary', require=False)

    tld = Option(doc='''
        **Syntax:** **tld=***<TLD ...>*
        **Description:** Swap TLD for the original domain
        ''', name='tld', require=False)

    fuzzers = Option(doc='''
        **Syntax:** **fuzzers=***<fuzzer ...>*
        **Description:** Use only selected fuzzing algorithms
        ''', name='fuzzers', require=False)

    def generate(self):
        domains = set()

        if self.csvfile:
            base_csvfile = os.path.basename(self.csvfile)
            csv_lookup_path = os.path.join(os.path.normpath(os.environ['SPLUNK_HOME']),
                                           'etc', 'apps', self.csvapp, 'lookups', base_csvfile)

            if csv_lookup_path != os.path.abspath(csv_lookup_path):
                self.write_error('Insecure path "{}"'.format(csv_lookup_path))
                return

            try:
                csv_reader = csv.DictReader(list(open(csv_lookup_path, 'r', newline='')))
            except OSError as err:
                self.write_error('Unable to open "{}" ({})'.format(csv_lookup_path, err.strerror))
                return
            else:
                for row in csv_reader:
                    if self.csvcol in row:
                        domains.add(row[self.csvcol])

        if self.fieldnames:
            domains.update(self.fieldnames)

        if not domains:
            self.write_info('Missing input domains')
            return

        explode = lambda s: list(filter(None, re.split(r' |,', str(s))))

        fuzzers = []
        if self.fuzzers:
            fuzzers = explode(self.fuzzers)

        dictionary = []
        if self.dictionary:
            dictionary = explode(self.dictionary)

        if dictionary and fuzzers and 'dictionary' not in fuzzers:
            self.write_info('Enabled dictionary fuzzer')
            fuzzers.append('dictionary')

        tld = []
        if self.tld:
            tld = explode(self.tld)

        if tld and fuzzers and 'tld-swap' not in fuzzers:
            self.write_info('Enabled tld-swap fuzzer')
            fuzzers.append('tld-swap')

        workers = min(len(domains), WORKERS)

        with Pool(workers) as pool:
            for domain, output in pool.imap_unordered(worker, zip(domains, repeat(fuzzers), repeat(dictionary), repeat(tld))):
                if isinstance(output, Exception):
                    self.write_warning('Exception occured while processing "{}": {}'.format(domain, str(output)))
                    continue
                tstamp = time.time()
                for permutation in output:
                    yield {
                        '_time': tstamp,
                        '_raw': permutation,
                        'fuzzer': permutation['fuzzer'],
                        'domain': permutation['domain'],
                        'origin': domain,
                    }


    def __init__(self):
        super(dnstwistCommand, self).__init__()


dispatch(dnstwistCommand, sys.argv, sys.stdin, sys.stdout, __name__)
