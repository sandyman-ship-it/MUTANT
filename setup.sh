#!/usr/bin/env bash

ENVNAME=$1

bash ./mutant/standalone/create_nf.sh
bash ./mutant/standalone/create_env.sh $ENVNAME
