#!/bin/bash

VERSION="3.7.1"

if [ "$(uname -m)" == "aarch64" ]; then
  SUFFIX="arm64"
else
  SUFFIX="64-bit"
fi

curl --remote-name --location "https://github.com/errata-ai/vale/releases/download/v${VERSION}/vale_${VERSION}_Linux_${SUFFIX}.tar.gz"
tar -xvzf "vale_${VERSION}_Linux_${SUFFIX}.tar.gz" -C "${HOME}/.local/bin"
rm "vale_${VERSION}_Linux_${SUFFIX}.tar.gz"
