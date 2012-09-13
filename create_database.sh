#!/bin/sh

DIRECTORY="$1"

if [ -z "$1" ] ; then
    echo "$0 <directory>"
    exit 1
fi

mkdir -p "$DIRECTORY/dbenv" "$DIRECTORY/data"
cat "`dirname $0`/imports.sql" | sqlite3 "$DIRECTORY/imports.sqlite"
