#!/usr/bin/env bash

bash ./mutant/assets/install/nextflow.sh
bash ./mutant/assets/install/conda.sh "D_mutant"

conda activate D_mutant
pip install -r requirements.txt
pip install -e .
