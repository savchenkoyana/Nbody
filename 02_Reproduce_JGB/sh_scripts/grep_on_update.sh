#!/usr/bin/env bash

# Check logfile
if [[ -z "$1" ]]; then
  echo "Usage: $0 <logfile>"
  exit 1
fi

LOGFILE="$1"

# print new lines with "ADJUST"
tail -F "$LOGFILE" | grep --line-buffered "ADJUST"
