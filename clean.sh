#!/bin/sh

echo "Cleaning Python bytecode files (*.pyc) ..."
find ./ -type f -name "*.pyc" -print -delete
