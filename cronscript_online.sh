#!/bin/bash

PY="/usr/bin/python3"

cd /var/www/html/boors/ > /dev/null

$PY make_current_signal.py >/dev/null
$PY my_make_signal.py >/dev/null

