#!/usr/bin/env bash

ENVNAME=$1

bash ./mutant/assets/install/nextflow.sh
bash ./mutant/assets/install/conda.sh $ENVNAME

conda activate $ENVNAME
pip install -r requirements.txt
pip install -e .
