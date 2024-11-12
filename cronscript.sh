#!/bin/bash

PY="/usr/bin/python3"

cd /var/www/html/boors/ > /dev/null

$PY get_stocks.py >/dev/null
$PY get_capital_risings.py > /dev/null
$PY fix_capital_risings.py >/dev/null
$PY make_signal.py >/dev/null

