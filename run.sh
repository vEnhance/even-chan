#!/bin/bash

cd "$(dirname "$0")" || exit
source ~/.virtualenvs/even-chan/bin/activate
python .
