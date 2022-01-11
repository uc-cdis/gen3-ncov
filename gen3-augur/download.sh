#!/bin/bash
set -e

today=$(date +'%m%d%y')
echo "Download files"

./gen3/gen3-client download-multiple --profile=covid19 --manifest=data/genomic_file_${today}_manifest.json --download-path=data/covid19_${today}_rawbg --skip-completed
