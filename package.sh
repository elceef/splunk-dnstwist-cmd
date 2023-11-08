#!/bin/sh -e

# Created by Marcin Ulikowski <marcin@ulikowski.pl>

# This script downloads and extracts required libraries, and then builds complete add-on package file

PACKAGE_NAME="SA_dnstwist.tgz"

SPLUNK_SDK_URL="https://files.pythonhosted.org/packages/ee/4a/e92bc2d09cbaafcf54f1226bb1e87988ab2c657cd65c9a9a081e94760b81/splunk-sdk-1.7.4.tar.gz"
IDNA_URL="https://files.pythonhosted.org/packages/8b/e1/43beb3d38dba6cb420cefa297822eac205a277ab43e5ba5d5c46faf96438/idna-3.4.tar.gz"
DNSTWIST_URL="https://files.pythonhosted.org/packages/ef/84/a1474ae1ec3ef3af0bbe6ee3bf6253570265835be8b3969301e07606481c/dnstwist-20230918.tar.gz"

ADDON_DIR="SA_dnstwist"
LIB="./$ADDON_DIR/lib"

if [ ! -d "$LIB" ]; then

  echo "Error: '$LIB' does not exist!"
  exit 1

fi

if [ -n "$(ls $LIB)" ]; then

  echo "Error: '$LIB' should be empty!"
  exit 1

fi

for i in wget tar gzip; do

  T=$(which "$i" 2>/dev/null)

  if [ "$T" = "" ]; then

    echo "Error: '$i' not found, please install first."
    exit 1

  fi

done

echo "Downloading Splunk-SDK from the web ..."
wget -nv -O - -- "$SPLUNK_SDK_URL" | \
tar --wildcards --no-wildcards-match-slash --strip-components=1 -xzf - -C "$LIB" "*/splunklib/*"

echo "Downloading IDNA from the web ..."
wget -nv -O - -- "$IDNA_URL" | \
tar --wildcards --no-wildcards-match-slash --strip-components=1 -xzf - -C "$LIB" "*/idna/*"

echo "Downloading dnstwist from the web ..."
wget -nv -O - -- "$DNSTWIST_URL" | \
tar --wildcards --no-wildcards-match-slash --strip-components=1 -xzf - -C "$LIB" "*/dnstwist.py"

echo "Building package ..."
COPYFILE_DISABLE=1 tar --format ustar --exclude="$0" --exclude="$PACKAGE_NAME" -cvzf "$PACKAGE_NAME" "$ADDON_DIR"

echo "Done!"

echo "Package file: $PACKAGE_NAME"

exit 0
