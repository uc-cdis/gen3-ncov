[![GitHub release (latest by date)](https://img.shields.io/github/v/release/nextstrain/ncov)](https://github.com/nextstrain/ncov/releases)
[![See recent changes](https://img.shields.io/badge/changelog-See%20recent%20changes-blue)](https://docs.nextstrain.org/projects/ncov/en/latest/reference/change_log.html)

# gen3-ncov

This repository is a forked repository of [Nextstrain ncov](https://github.com/nextstrain/ncov). This repository contains a collection of tools to perform customized phylogenomic analysis on Illinois covid19 viral sequences hosted at [Chicago land Pandemic Response Commons (PRC)](https://chicagoland.pandemicresponsecommons.org/). The visualization of this workflow output can be deployed at PRC data commons using [gen3-auspice](https://github.com/uc-cdis/gen3-auspice)

# About nextstrain/ncov workflow

Detailed instruction about workflow setup, data preparation, customizing analysis, as well as results interpretation can be found [HERE](https://docs.nextstrain.org/projects/ncov/en/latest/analysis/index.html)

# Running gen3-ncov worklfow

## Setup conda env
For faster installation, update Conda to the latest version and install `Mamba`. 
```
conda update -n base conda
conda install -n base -c conda-forge manba
```
Create a virtual conda environment. The command below installs all the nexstrain tools as well as gen3-augur query tools
```
# change directory under gen3-ncov folder
cd gen3-ncov
mamba env create -n {env_name} -f ./environment.yml
```
Confirm that installation works
```
conda activate {env_name}
nextstrain check-setup --set-default
```
Edit file of `set_env_var.sh` and add the path of PRC credentials to the variable `GEN3_API_KEY`. The PRC credentials (json format) can be downloaded from the profile page after Login to [PRC data commons](https://chicagoland.pandemicresponsecommons.org/). After saving the file, run the command line below.
```
source set_env_var.sh
# To confirm env variable
echo $GEN3_API_KEY
echo $project_id
```
## Run analysis workflow
To get the phylogenetic tree including all Illinois covid19 strains hosted at PRC data commons. Simply run
```
bash build_il_siu_tree.sh
```
- This bash script uses the profile of `IL_SIU_tree` under `./my_profiles` folder
- This script uses the gen3-client command-line tool to download object file from PRC commons. The tool included in this repo is compatible with linux system. To get the gen3-client for windows and OSX, visit [cdis-data-client](https://github.com/uc-cdis/cdis-data-client)
- This workflow performs the analysis with all IL covid19 strains submitted to [PRC data commons](https://chicagoland.pandemicresponsecommons.org/) without subsampling scheme.
- To run a quicker analysis with subsampling scheme, run the command below after downloading step is done.
```
nextstrain build . --configfile my_profiles/IL_SIU_tree_subsampling/builds.yaml
```
