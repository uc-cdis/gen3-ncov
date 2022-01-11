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

# Query manifest
echo "Query Manifest"
expect_files=$(gen3-augur Gen3Query --url "${endpoint}/" --type genomic_file --fields file_name,file_size,md5sum,object_id --filter project_id --value "${project_id}" --format json --logfile genomic_manifest_${today})

# Setup up gen3-client
echo "Setup gen3-client"
./gen3/gen3-client configure --profile=covid19 "--cred=${GEN3_API_KEY}" --apiendpoint=${endpoint}/

# Download object files
echo "Download object files"
mkdir -p data/covid19_${today}_rawbg
exist_files=$(ls data/covid19_${today}_rawbg|wc -l)

while [ ${exist_files} -lt ${expect_files} ];
do
    echo ${expect_files}
    echo ${exist_files}
    echo y|bash download.sh
    exist_files=$(ls data/covid19_${today}_rawbg|wc -l)
done;

# Substitute '/' to '_' in header for all fasta file
cd data/covid19_${today}_rawbg
for filename in *; do sed -i "" "s/\//_/g" ${filename}; done
cd ../../

# Merge multiple fasta into one fasta file
echo "Merge fasta file"
cat data/covid19_${today}_rawbg/*.fasta >> data/covid19_${today}.fasta

# Query metadata, generate metadata.csv
echo "Query Metadata"
expect_files=$(gen3-augur Gen3Query --url "${endpoint}/" --type genomic_file --fields nextstrain_clade,zipcode,continent,country_region,province_state,county,host,organism,sample_type,isolation_source,isolate,collection_date,originating_lab,submitting_lab,submitting_lab_PI,submitter_id,file_name,file_size,md5sum,object_id --filter project_id --value "${project_id}" --format csv --logfile sample_manifest_${today})

# Run Augur pipeline
# Alignment(default mafft tool)
echo "Run alignment"
mkdir results/covid19_${today}_translations
nextalign --reference config/sequence.fasta --genemap config/annotation.gff.txt --genes "ORF1a,ORF1b,S,ORF3a,M,N" --sequences data/covid19_${today}.fasta --output-dir results/covid19_${today}_translations --output-basename aligned --output-fasta results/covid19_${today}_aligned.fasta --output-insertions results/covid19_${today}_insertions.tsv

# Scan aligned sequences for problematic sequences
python scripts/diagnostic.py --alignment results/covid19_${today}_aligned.fasta --metadata data/genomic_file_${today}_manifest.csv --reference config/sequence.gb --mask-from-beginning 100 --mask-from-end 50 --output-flagged results/covid19_${today}_flagged-sequences.tsv --output-diagnostics results/covid19_${today}_sequence-diagnostics.tsv --output-exclusion-list results/covid19_${today}_to-exclude.txt

# Mask bases in alignment
python scripts/mask-alignment.py --alignment results/covid19_${today}_aligned.fasta --mask-from-beginning 100 --mask-from-end 50 --mask-terminal-gaps --output results/covid19_${today}_masked_aligned.fasta 2>&1 | tee logs/run_pipeline_${today}.log

# Filter alignment
echo "Filter alignment"
augur filter --sequences results/covid19_${today}_masked_aligned.fasta --metadata data/genomic_file_${today}_manifest.csv --exclude results/covid19_${today}_to-exclude.txt --output results/covid19_${today}_filter_aligned.fasta 2>&1 | tee logs/run_pipeline_${today}.log

# Run pangolin
pangolin results/covid19_${today}_filter_aligned.fasta --outdir results/covid19_${today}_pangolin --outfile pangolineages.csv 2>&1 | tee logs/run_pipeline_${today}.log

python scripts/make_pangolin_node_data.py --pangolineages results/covid19_${today}_pangolin/pangolineages.csv --node_data_outfile results/covid19_${today}_pangolin/pangolineages.json

# Create raw tree
echo "Create raw tree"
augur tree --alignment results/covid19_${today}_filter_aligned.fasta --output results/covid19_${today}_tree_raw.nwk --tree-builder-args '-ninit 10 -n 4' --nthreads auto 

# Refine tree
echo "Refine tree"
augur refine --tree results/covid19_${today}_tree_raw.nwk --alignment results/covid19_${today}_filter_aligned.fasta --metadata data/genomic_file_${today}_manifest.csv --output-tree results/covid19_${today}_tree.nwk --output-node-data results/covid19_${today}_branch_lengths.json --timetree --coalescent skyline --date-confidence --date-inference marginal --clock-filter-iqd 4 --root oldest --clock-rate 0.0008 --clock-std-dev 0.0004 --divergence-unit "mutations" --no-covariance

# Ancestry Inference
echo "Infer ancestry sequence and mutation"
augur ancestral --tree results/covid19_${today}_tree.nwk --alignment results/covid19_${today}_filter_aligned.fasta --output-node-data results/covid19_${today}_nt_muts.json --inference joint --infer-ambiguous 2>&1 | tee logs/run_pipeline_${today}.log

# Translating amino acid sequences
echo "Mutation translation"
augur translate --tree results/covid19_${today}_tree.nwk --ancestral-sequences results/covid19_${today}_nt_muts.json --reference-sequence config/sequence.gb --output results/covid19_${today}_aa_muts.json 2>&1 | tee logs/run_pipeline_${today}.log

# Mutation summary
python scripts/mutation_summary.py --alignment results/covid19_${today}_filter_aligned.fasta --insertions results/covid19_${today}_insertions.tsv --directory results/covid19_${today}_translations --basename "aligned" --reference config/sequence.fasta --genemap config/annotation.gff.txt --genes "ORF1a" "ORF1b" "S" "ORF3a" "M" "N" --output results/covid19_${today}_mutation_summary.tsv 2>&1 | tee logs/run_pipeline_${today}.log

# Translating amino acid sequences
python scripts/explicit_translation.py --tree results/covid19_${today}_tree.nwk --translations results/covid19_${today}_translations/aligned.gene.S.fasta results/covid19_${today}_translations/aligned.gene.ORF1a.fasta results/covid19_${today}_translations/aligned.gene.ORF1b.fasta results/covid19_${today}_translations/aligned.gene.ORF3a.fasta results/covid19_${today}_translations/aligned.gene.M.fasta results/covid19_${today}_translations/aligned.gene.N.fasta --genes "ORF1a" "ORF1b" "S" "ORF3a" "M" "N" --output results/covid19_${today}_aa_muts_explicit.json

# Distance
augur distance --tree results/covid19_${today}_tree.nwk --alignment results/covid19_${today}_translations/aligned.gene.S_withInternalNodes.fasta --gene-names 'S' --compare-to 'root' --attribute-name 'S1_mutations' --map "config/distance_maps/S1.json" --output results/covid19_${today}_distances.json

# Refine traits
echo "Refine traits"
augur traits --tree results/covid19_${today}_tree.nwk --metadata data/genomic_file_${today}_manifest.csv --output results/covid19_${today}_traits.json --columns location --confidence

# Labeling clades as specified in config/clades.tsv
augur clades --tree results/covid19_${today}_tree.nwk --mutations results/covid19_${today}_nt_muts.json results/covid19_${today}_aa_muts.json --clades config/clades.tsv --output-node-data results/covid19_${today}_clade.json

# emerging_lineage
augur clades --tree results/covid19_${today}_tree.nwk  --mutations results/covid19_${today}_nt_muts.json results/covid19_${today}_aa_muts.json --clade config/emerging_lineages.tsv --output-node-data results/covid19_${today}_emerging_lineages.json

# Rename emerging_lineage
python scripts/remane_emerging_lineage.py --file results/covid19_${today}_emerging_lineages.json

# Constructing colors file
#python scripts/assign-colors.py --ordering config/color_ordering.tsv --color-schemes config/color_schemes.tsv --output results/covid19_${today}_colors.tsv --metadata data/genomic_file_${today}_manifest.csv

# Frequncy
echo "Frequency json"
augur frequencies --method kde --metadata data/genomic_file_${today}_manifest.csv --tree results/covid19_${today}_tree.nwk --output results/covid19_${today}_tip-frequencies.json 

#logistic_growth 
python scripts/calculate_delta_frequency.py --tree results/covid19_${today}_tree.nwk --frequencies results/covid19_${today}_tip-frequencies.json --method "logistic" --delta-pivots 6 --min-tips 50 --min-frequency 0.000001 --max-frequency 0.95 --attribute-name "logistic_growth" --output results/covid19_${today}_logistic_growth.json

# Export json
echo "Export json"
augur export v2 --tree results/covid19_${today}_tree.nwk --metadata data/genomic_file_${today}_manifest.csv --node-data results/covid19_${today}_branch_lengths.json results/covid19_${today}_nt_muts.json results/covid19_${today}_aa_muts.json results/covid19_${today}_emerging_lineages.json results/covid19_${today}_clade.json results/covid19_${today}_traits.json results/covid19_${today}_logistic_growth.json results/covid19_${today}_aa_muts_explicit.json results/covid19_${today}_distances.json results/covid19_${today}_pangolin/pangolineages.json --colors config/color_schemes.tsv --lat-longs config/latitude_longitude.tsv --auspice-config config/auspice_config.json --output auspice/covid19_${today}.json

python scripts/add_branch_labels.py --input auspice/covid19_${today}.json --emerging-clades results/covid19_${today}_emerging_lineages.json --output auspice/covid19_${today}_with_branch_labels.json

mv results/covid19_${today}_tip-frequencies.json auspice/covid19_${today}_with_branch_labels_tip-frequencies.json
