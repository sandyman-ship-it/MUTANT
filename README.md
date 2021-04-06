# MUTANT
Microbial Utility Toolbox And wrapper for data traNsmission and Transformation

## Installation

### Prereq
* Install Java 8 or above (`java --version`)
* Install singularity (`conda install -c conda-forge singularity`)
* Install nextflow (`curl -s https://get.nextflow.io | bash`)
* Path nextflow (`export PATH=$PATH:/MY/WORKING/DIR`)

### Setup
* `git clone --recurse-submodules --branch main https://github.com/Clinical-Genomics/MUTANT.git`
* `cd MUTANT && source setup.sh D_mutant` 
* `source activate D_mutant`
* `mutant toolbox sarscov2images`

## Development

### Self-test
* `source activate D_mutant`
* `mutant analyse sarscov2 tests/testdata/fasta_files --profiles local,singularity --config_artic mutant/config/local/artic.json --config_mutant mutant/config/local/mutant.json` 
* Wait for pipeline completion (~3m). Check results in `./results/` 

### Version bumping

MUTANTs versioning is bumped manually post PR merge, using [semver](https://semver.org/) standards on [this](https://github.com/Clinical-Genomics/MUTANT/blob/main/mutant/__init__.py#L3) variable.

## Updating

* `INSTANCE='stage'` or `INSTANCE='production'`
* `cd /home/proj/${INSTANCE}/mutant/MUTANT`
* `git pull origin main`
* `INITIAL="$(echo $word | head -c 1)"`
* `source activate ${INITIAL}_mutant`
* `pip install -e .`

