#!/bin/sh

if [ ! "$1" ]; then
    echo "Please specify a db."
    exit
fi

if [ "$2" = save ]; then
    while true; do
        sage -python automate.py $1 $2 $3 $4 $5
    done
fi
