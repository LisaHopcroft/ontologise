#!/bin/bash

python parse.py -i "data/p2833, Felicity.txt"

python parse.py -i "data/p2833, Felicity with new format sample.txt"

python parse.py -i "data/p2833, Felicity with new format multiple shortcuts stop_at_global_id.txt" -s settings2.yaml
