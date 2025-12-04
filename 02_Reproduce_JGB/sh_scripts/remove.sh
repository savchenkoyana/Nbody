#!/bin/bash

# Check if a path argument was provided
if [ $# -eq 0 ]; then
    echo "Removes 'conf.3_*', 'comm.2_*', and 'snap.40_*' from directories"
    echo "Usage: $0 <relative_path_pattern>"
    echo "Example: $0 ./N5000_MA*"
    exit 1
fi

# Process all arguments
for RELATIVE_PATH in "$@"; do
    # Check if the path exists
    if [ ! -d "$RELATIVE_PATH" ]; then
        echo "Warning: Path '$RELATIVE_PATH' does not exist or is not a directory, skipping"
        continue
    fi

    # Delete the specified file patterns
    echo "Deleting files in: $RELATIVE_PATH"

    find "$RELATIVE_PATH/" -name "conf.3_*" -delete
    find "$RELATIVE_PATH/" -name "comm.2_*" -delete
    find "$RELATIVE_PATH/" -name "snap.40_*" -delete

    echo "Cleanup completed for: $RELATIVE_PATH"
    echo "---"
done
