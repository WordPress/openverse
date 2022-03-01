#!/usr/bin/env bash
UPDATE=''
while getopts ":u" arg; do
  case "${arg}" in
    u)
      UPDATE='--update-tapes'
        ;;
      *)
        ;;
  esac
done
echo "Start e2e test";
node test/proxy.js $UPDATE & TALKBACK_PID=$!
if pnpm run build-and-e2e; then
  kill -17 $TALKBACK_PID;
  echo "E2e tests passed successfully; talkback proxy stopped";
else
  echo "E2e tests failed";
  kill -9 $TALKBACK_PID;
  exit 1;
fi
