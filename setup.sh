#!/usr/bin/env bash

source ./mutant/assets/nextflow.sh
bash ./mutant/assets/conda.sh

conda activate mutant
pip install .
