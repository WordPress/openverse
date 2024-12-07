#!/bin/bash

BIN_NAME="$1"
VERSION="3.7.1"
OS=$([ "$(uname)" = "Darwin" ] && echo "macOS" || echo "Linux")
ARCH=$([ "$(uname -m)" = "aarch64" ] || [ "$(uname -m)" = "arm64" ] && echo "arm64" || echo "64-bit")

URL="https://github.com/errata-ai/vale/releases/download/v${VERSION}/vale_${VERSION}_${OS}_${ARCH}.tar.gz"

echo "Downloading ${URL}"
curl --output vale.tar.gz --location "${URL}"
tar -xvzf "vale.tar.gz" vale
mv vale "${BIN_NAME}"
rm "vale.tar.gz"
