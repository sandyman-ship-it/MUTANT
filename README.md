# MUTANT
Microbial Utility Toolbox And wrapper for data traNsmission and Transformation

## Prereq
* `Install java 8 or above`
* `Install singularity (conda install -c conda-forge singularity`

## Setup
* `git clone --recurse-submodules --branch main https://github.com/Clinical-Genomics/MUTANT.git`
* `cd MUTANT && source setup.sh D_mutant` 

## Self-test
Add the MUTANT directory to your path. Execute using:

* `source activate D_mutant`
* `mutant analyse sarscov2 tests/testdata/fasta_files --profiles local,singularity --config_artic mutant/config/local/artic.json` 
* `Wait 3m. Check results in ./results/` 

## Version bumping

MUTANTs versioning is bumped manually post PR merge, using (semver rules)[https://semver.org/] on [this](https://github.com/Clinical-Genomics/MUTANT/blob/main/mutant/__init__.py#L3) variable.
