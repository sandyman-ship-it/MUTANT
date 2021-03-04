""" CLI access point for various MICROBIAL tools 
    By: Isak Sylvin @sylvinite & C:/O """


#!/usr/bin/env python

import click
import os
import re
import subprocess
import sys

from datetime import datetime
from mutant import version, log

#File work directory
WD = os.path.dirname(os.path.realpath(__file__))
TIMESTAMP = datetime.timestamp( datetime.now() ) 

@click.group()
@click.version_option(version)
@click.pass_context
def root(ctx):
    """ Microbial Utility Toolbox And wrapper for data traNsmission and Transformation """
    ctx.obj = {}

@root.group()
@click.pass_context
def analyse(ctx):
    pass

@analyse.command()
@click.argument("input_folder")
@click.option("--config_case", help="Provided config case",default="")
@click.option("--outdir", help="Output folder", default="/tmp/")
@click.pass_context
def sarscov2(ctx, input_folder, config_case, outdir):
    #Derive prefix from config-case; else use default
    prefix = "artic-{}".format(TIMESTAMP)
    if config_case != "":
        #Generate prefix dynamically from config-case
        pass

    cmd = 'nextflow run {0}/externals/ncov2019-artic-nf/main.nf -profile singularity --illumina --prefix "{1}" --directory {2} --outdir {3}'\
            .format(WD, prefix, input_folder, outdir)
    log.debug("Command ran: {}".format(cmd))
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    out, err = proc.communicate()
    log.info(out)
    log.info(err)


@analyse.command()
@click.pass_context
def jasen(ctx):
    pass

@root.group()
@click.pass_context
def toolbox(ctx):
    pass
