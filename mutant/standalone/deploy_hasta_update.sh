#!/usr/bin/env bash

SCRIPT=$(readlink -f $0)
scriptdir=`dirname $SCRIPT`
INSTANCE=$1

OLDDIR=pwd

INSTANCE='stage' or INSTANCE='production'
cd /home/proj/${INSTANCE}/mutant/MUTANT
git checkout main
git pull origin main
INITIAL="$(echo $INSTANCE | head -c 1)"
source activate ${INITIAL^}_mutant
pip install -e .
source deactivate
cd $OLDDIR
