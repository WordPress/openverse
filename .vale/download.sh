#!/bin/bash

VERSION="3.7.1"

if [ "$(uname)" = "Darwin" ]; then
  OS="macOS"
else
  OS="Linux"
fi

if [ "$(uname -m)" = "aarch64" ] || [ "$(uname -m)" = "arm64" ]; then
  ARCH="arm64"
else
  ARCH="64-bit"
fi

URL="https://github.com/errata-ai/vale/releases/download/v${VERSION}/vale_${VERSION}_${OS}_${ARCH}.tar.gz"

echo "Downloading ${URL}"
curl --output vale.tar.gz --location "${URL}"
tar -xvzf "vale.tar.gz" vale
rm "vale.tar.gz"
