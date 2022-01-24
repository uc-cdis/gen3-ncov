#!/bin/sh
set -ex

today=$(date +'%m%d%y')

if [[ -z "$GEN3_API_KEY" || ! -f "$GEN3_API_KEY" ]]; then
  echo "GEN3_API_KEY ($GEN3_API_KEY) does not exist"
  echo "NOTE: do not place an api key file"
  echo "    under a github managed folder."
  exit 1
fi

endpoint="https://chicagoland.pandemicresponsecommons.org/"

project_id="Walder-SIU-SARS-CoV2"

# Query genomic file manifest
echo "Query Genomic File Manifest"
expect_files=$(gen3-augur Gen3Query --url "${endpoint}/" --type genomic_file --fields file_name,file_size,md5sum,object_id --filter project_id --value "${project_id}" --format json --logfile genomic_manifest_${today})

# setup gen3-client
echo "Setting up prc profile in gen3-client"
./gen3-client/gen3-client configure --profile=covid19 "--cred=${GEN3_API_KEY}" --apiendpoint=${endpoint}/

# Download genomic object file
echo "Download object files"
mkdir -p ./gen3-augur/data/covid19_${today}_rawbg
exist_files=$(ls ./gen3-augur/data/covid19_${today}_rawbg|wc -l)

while [ ${exist_files} -lt ${expect_files} ];
do
    echo ${expect_files}
    echo ${exist_files}
    echo y|bash gen3-augur/download.sh
    exist_files=$(ls gen3-augur/data/covid19_${today}_rawbg|wc -l)
done;

# substitue ??? with NA ub geader for all fasta file
cd ./gen3-augur/data/covid19_${today}_rawbg
for filename in *; do sed -i "s/???/NA/g" ${filename}; done
for filename in *; do sed -i "s/_/\//g" ${filename}; done
cd ../../..

# Merge all fasta files into one fasta
echo "Merge fasta files"
cat ./gen3-augur/data/covid19_${today}_rawbg/*.fasta >> data/covid19_IL_sequence.fasta

# Query metadata, generate metadata.csv
echo "Query Metadata"
expect_files=$(gen3-augur Gen3Query --url "${endpoint}/" --type genomic_file --fields nextstrain_clade,zipcode,continent,country_region,province_state,county,host,organism,sample_type,isolation_source,isolate,collection_date,originating_lab,submitting_lab,submitting_lab_PI,submitter_id,file_name,file_size,md5sum,object_id --filter project_id --value "${project_id}" --format tsv --logfile sample_manifest_${today})
cp ./gen3-augur/data/genomic_file_${today}_manifest.tsv ./data/covid19_IL_metadata.tsv

# Run nextstrain ncov workflow to build an IL tree without subsampling. The output will be stored under auspice/ folder
nextstrain build . --configfile my_profiles/IL_SIU_tree/builds.yaml

# Build an IL tree with subsampling scheme, uncomment the line below
#nextstrain build . --configfile my_profiles/IL_SIU_tree_subsampling/builds.yaml
