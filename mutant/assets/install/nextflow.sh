#!/usr/bin/env bash

# curl -s https://get.nextflow.io | bash

scriptdir="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
if [[ ${PATH} != *"${scriptdir}"* ]]; then
    export PATH=$PATH:$scriptdir
fi

