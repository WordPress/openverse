#!/bin/bash

red="\e[31m"
green="\e[32m"
endcol="\e[0m"

# Specify a file as the first argument to restrict the test to that file only.
# ```
# $	./test/run_test.sh test/audio_integration_test.py
# ```
if [ $# -ge 1 ]; then
	TEST_ARG="$@"
else
	TEST_ARG="test/"
fi

PYTHONWARNINGS="ignore:Unverified HTTPS request" \
PYTHONPATH=. \
pytest -s --disable-pytest-warnings $TEST_ARG

succeeded=$?
if [[ $succeeded -eq 0 ]]; then
    printf "${green}:-) All tests passed${endcol}\n"
else
    printf "\n\n${red}:'( Some tests did not pass${endcol}\n"
    printf "Hint: \`just logs [service]\` will print the Docker logs and may be helpful for debugging.\n\n"
fi
exit $succeeded
