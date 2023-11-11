dnstwist add-on (command)
=========================

This Splunk add-on enhances functionality with a custom `| dnstwist` command,
enabling the generation of an extensive set of lookalike and potentially
malicious domain permutations.


Usage examples
--------------

Generate permutations from a list of domains. If the list contains a valid URL
or email address, domain names will be automatically extracted.

```
| dnstwist splunk.com https://dnstwist.it
```

Generate permutations of domains stored under column *domain* (default) in CSV
lookup file named *domains.csv* stored in *search* app. In this case the loaded
file will be: `$SPLUNK_HOME/etc/apps/search/lookup/domains.csv`.

```
| dnstwist csvfile=domains.csv csvapp=search csvcol=domain
```

Input domains can be ingested from various sources simultaneously.

```
| dnstwist splunk.com dnstwist.it csvfile=domains.csv
  [| inputlookup domains.csv| stats values(domain) as domains| return $domains]
```

Domain permutations can be limited to only selected fuzzing algorithms provided
as a list separated with spaces or commas. Non-existent algorithm names will be
silently ignored.

```
| dnstwist fuzzers="homoglyph hyphenation subdomain" splunk.com
```

Supply dictionary words to generate additional permutations. This option
enables dedicated fuzzing algorithm.

```
| dnstwist dictionary="secure support www login auth" splunk.com
```

Alternatively, dictionary words can be loaded with a subsearch.

```
| dnstwist splunk.com
  [| inputlookup words.csv | stats values(word) as dictionary | return dictionary]
```
