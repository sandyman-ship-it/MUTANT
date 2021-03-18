#!/usr/bin/env bash

source ./mutant/assets/install/nextflow.sh
bash ./mutant/assets/install/conda.sh

conda activate mutant
pip install .
