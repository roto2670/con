#!/bin/sh

OUTPUT_DIR=~/Desktop/doc_output/console

cd .. &&
mkdir -p $OUTPUT_DIR &&
apidoc -i . -o $OUTPUT_DIR -f src/openapi/routes.py
