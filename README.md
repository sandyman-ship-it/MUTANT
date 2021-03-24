# MUTANT
Microbial Utility Toolbox And wrapper for data traNsmission and Transformation

## Setup
* `Install java 8 or above`
* `git clone --recurse-submodules --branch main https://github.com/Clinical-Genomics/MUTANT.git`
* `cd MUTANT && source setup.sh D_mutant` 

## Self-test
Add the MUTANT directory to your path. Execute using:

`mutant analyse sarscov2 tests/testdata/fasta_files --profiles local,singularity --config mutant/config/local/artic.json`  
