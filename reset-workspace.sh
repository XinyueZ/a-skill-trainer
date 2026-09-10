#!/bin/bash
set -e

TARGET_DIR=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -d|--dir|--workspace)
      TARGET_DIR="$2"
      shift 2
      ;;
    *)
      if [ -z "$TARGET_DIR" ]; then
        TARGET_DIR="$1"
        shift 1
      else
        echo "❌ Unknown parameter: $1"
        exit 1
      fi
      ;;
  esac
done

if [ -z "$TARGET_DIR" ]; then
  echo "❌ Error: Target directory must be specified!"
  echo "Usage: $0 <path> or $0 --dir <path>"
  exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
  echo "❌ Error: Target directory does not exist: $TARGET_DIR"
  exit 1
fi

ABS_TARGET_DIR=$(cd "$TARGET_DIR" && pwd)

if ! git -C "$ABS_TARGET_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Error: '$ABS_TARGET_DIR' is not a valid Git repository!"
  exit 1
fi

INIT_COMMIT=$(git -C "$ABS_TARGET_DIR" rev-list --max-parents=0 HEAD | tail -n 1)

if [ -z "$INIT_COMMIT" ]; then
  echo "❌ Error: Failed to find initial commit!"
  exit 1
fi

echo "🔄 Resetting repository at: $ABS_TARGET_DIR"
echo "📌 Target initial commit ID: $INIT_COMMIT"

git -C "$ABS_TARGET_DIR" reset --hard "$INIT_COMMIT"
git -C "$ABS_TARGET_DIR" clean -fd

echo "✨ Success: Repository fully reset to initial commit. Working tree is clean!"