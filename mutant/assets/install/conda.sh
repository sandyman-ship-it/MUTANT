#!/usr/bin/env bash

SCRIPT=$(readlink -f $0)
scriptdir=`dirname $SCRIPT`
NAME=$1
conda env create --name $NAME -f $scriptdir/environment.yaml
