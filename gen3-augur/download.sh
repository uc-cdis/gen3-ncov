#!/bin/bash
set -e

today=$(date +'%m%d%y')
echo "Download files"

./gen3-client/gen3-client download-multiple --profile=covid19 --manifest=gen3-augur/data/genomic_file_${today}_manifest.json --download-path=gen3-augur/data/covid19_${today}_rawbg --skip-completed
