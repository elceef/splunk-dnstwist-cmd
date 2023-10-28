dnstwist add-on (command)
=========================

This Splunk add-on provides custom `| dnstwist` command which generates a large
set of lookalike domain permutations.


Installation
------------

The build script downloads and extracts required libraries, and then produces
a complete and ready to install add-on package file:

```
$ bash ./package.sh
```

When package file is ready, either unpack it to `$SPLUNK_HOME/etc/apps` on
Splunk search head or use the CLI to install it.


Examples
--------

Generate permutations from a list of domains. If the list contains a valid URL
or email address, domain names will be automatically extracted.

```
| dnstwist splunk.com https://dnstwist.it
```

Generate permutations of domains stored under column *domain* (default) in CSV
lookup file. In this case `$SPLUNK_HOME/etc/apps/search/lookup/domains.csv`.

```
| dnstwist csvfile=domains.csv csvapp=search csvcol=domain
```

Input domains can be ingested from various sources simultaneously.

```
| dnstwist splunk.com csvfile=domains.csv
  [| inputlookup domains.csv| stats values(domain) as domains| return $domains]
```

Domain permutations can be limited to only selected fuzzing algorithms provided
as a list separated with spaces or commas.

```
| dnstwist fuzzers="homoglyph hyphenation subdomain" splunk.com
```

Supply dictionary words to generate additional permutations. This argument
enables dedicated fuzzing algorithm.

```
| dnstwist dictionary="secure support www login auth" splunk.com
```

Alternatively, dictionary words can be loaded with a subsearch.

```
| dnstwist splunk.com
  [| inputlookup words.csv | stats values(word) as dictionary | return dictionary]
```
