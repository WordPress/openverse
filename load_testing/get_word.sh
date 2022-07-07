#! /usr/bin/env sh

python -c "from urllib import parse; print(parse.urlencode({'q': \"$(shuf -n1 /usr/share/dict/words)\"}), end='')"
