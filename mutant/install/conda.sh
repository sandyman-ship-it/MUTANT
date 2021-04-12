#!/usr/bin/env bash

SCRIPT=$(readlink -f $0)
scriptdir=`dirname $SCRIPT`
NAME=$1

echo "INFO - Unloading active environment"
conda info| tac | tac | grep -q $NAME && source deactivate || :
echo "INFO - Removing existing instance of environment (if present)"
conda remove -y -n $NAME --all || :

echo "INFO - Creating new environment"
conda create --yes --name $NAME python=3.7
source activate $NAME

echo "INFO - Installing requirements"
conda config --add channels bioconda
pip install -r ${scriptdir}/../../requirements-pip.txt
conda install --yes --file ${scriptdir}/../../requirements-conda.txt

echo "INFO - Installing MUTANT"
pip install -e .
echo "INFO - Installation complete!"

