#!/bin/bash

# Check if a path argument was provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <relative_path>"
    echo "Example: $0 ./N5000_r1_noGr_noext_v3_restart8"
    exit 1
fi

RELATIVE_PATH="$1"

# Check if the path exists
if [ ! -d "$RELATIVE_PATH" ]; then
    echo "Error: Path '$RELATIVE_PATH' does not exist or is not a directory"
    exit 1
fi

# Delete the specified file patterns
echo "Deleting files in: $RELATIVE_PATH"
rm -rf "$RELATIVE_PATH"/conf.3_*
rm -rf "$RELATIVE_PATH"/comm.2_*
rm -rf "$RELATIVE_PATH"/snap.40_*

echo "Cleanup completed for: $RELATIVE_PATH"
