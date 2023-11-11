dnstwist add-on (command)
=========================

This Splunk add-on enhances functionality with a custom `| dnstwist` command,
enabling the generation of an extensive set of lookalike and potentially
malicious domain permutations.


Installation
------------

Execute build script which will download required libraries, and then produce
a complete and ready to install add-on package:

```
$ sh ./package.sh
```

When the package file is ready, either unpack it to `$SPLUNK_HOME/etc/apps` on
Splunk search head or use the CLI to install it.


Compatibility
-------------

Splunk Enterprise 8.x or newer is required.
