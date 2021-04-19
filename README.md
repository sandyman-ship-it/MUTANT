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
* `mutant toolbox sarscov2images` (This does currently not work on hasta. WORKAROUND: Use this command on another computer and transfer the generated img files)

## Development

* Put your changes in a branch. Make a Pull Request of said branch
* Run the `self-test`
* Fill in everything you can in the PR template
* Ping `@sylvinite` in some way and tell him said PR is done.
* `@sylvinite` will review your PR & suggest changes
* Integrate said changes. If the changes are only aestetic, simply mention you're done without rerunning any tests
* `@sylvinite` will merge your changes and version bump. `@sylvinite` will deploy, however, it is appreciated to pitch in if able.

### Self-test
* `source activate D_mutant`
* `mutant analyse sarscov2 tests/testdata/fasta_files --profiles local,singularity --config_artic mutant/config/local/artic.json --config_mutant mutant/config/local/mutant.json` 
* Wait for pipeline completion (~3m). Check results in `./results/` 

### Version bumping

MUTANTs versioning is bumped manually post PR merge, using [semver](https://semver.org/) standards on [this](https://github.com/Clinical-Genomics/MUTANT/blob/main/mutant/__init__.py#L3) variable.

## Deploying new version

* `INSTANCE='stage'` or `INSTANCE='production'`
* `cd /home/proj/${INSTANCE}/mutant/MUTANT`
* `git checkout main`
* `git pull origin main`
* `INITIAL="$(echo $word | head -c 1)"`
* `source activate ${INITIAL}_mutant`
* `pip install -e .`

