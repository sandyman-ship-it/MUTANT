#!/usr/bin/env bash

ENVNAME=$1

bash ./mutant/install/nextflow.sh
bash ./mutant/install/conda.sh $ENVNAME

conda activate $ENVNAME
pip install -r requirements.txt
pip install -e .
