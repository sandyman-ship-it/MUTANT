""" CLI access point for various MICROBIAL tools 
    By: Isak Sylvin @sylvinite & C:/O """


#!/usr/bin/env python

import os
import sys
import re
import click
import json
import subprocess
from datetime import datetime
from mutant import version, log
from mutant.assets.deliver.deliver_artic import DeliverSC2

#File work directory
WD = os.path.dirname(os.path.realpath(__file__))
TIMESTAMP = datetime.now().strftime("%y%m%d-%H%M%S")

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
@click.option("--config", help="Custom artic configuration file", default="{}/config/hasta_artic.config".format(WD))
@click.option("--config_case", help="Provided config case", default="")
@click.option("--outdir", help="Output folder", default="results")
@click.option("--profiles", help="Execution profiles, comma-separated", default="singularity,slurm")
@click.pass_context
def sarscov2(ctx, input_folder, config_case, config, outdir, profiles):

    # Get sample information from config_case or use default values
    if config_case != "":
        caseinfo = get_config_data(config_case)
        prefix = "{}_{}".format(caseinfo[0]["case_ID"], TIMESTAMP)
        #Check that all samples have the same region and lab code
    else:
        prefix = "artic_{}".format(TIMESTAMP)

    # Set nextflow config
    confline = ""
    if config != "":
        config = os.path.abspath(config)
        confline = "-C {0}".format(config)

    # Run Artic
    cmd = 'nextflow {0} run {1}/externals/ncov2019-artic-nf/main.nf -profile {2} --illumina --prefix {3} --directory {4} --outdir {5}'\
            .format(confline, WD, profiles, prefix, input_folder, outdir)
    log.debug("Command ran: {}".format(cmd))
    proc = subprocess.Popen(cmd.split())
    out, err = proc.communicate()
    log.info(out)
    log.info(err)

    # Reports
    # Json
    # Deliverables
    if config != "":
        delivery = DeliverSC2(
            caseinfo=caseinfo,
            resdir=os.path.abspath(outdir),
            TIMESTAMP=TIMESTAMP
        )
        delivery.rename_deliverables()
        delivery.gen_delivery(prefix)
    print("Done")

@analyse.command()
@click.pass_context
def jasen(ctx):
    pass

@root.group()
@click.pass_context
def toolbox(ctx):
    pass

@toolbox.command()
@click.argument("input_folder")
@click.argument("ticket_number")
def ArticReport(input_folder, ticket_number):
    """ Custom report from the QC output of the ARTIC pipeline, applied on SARS-CoV-2 samples """
    cmd = "python {0}/assets/artic_report.py {1} {2}".format(WD, input_folder, ticket_number)
    log.debug("Command ran: {}".format(cmd))
    proc = subprocess.Popen(cmd.split())
    out, err = proc.communicate()

def get_config_data(config):
    if os.path.exists(config):
        """Get sample information as json object"""
        try:
            with open(config) as json_file:
                data = json.load(json_file)
        except Exception as e:
            click.echo("Unable to read provided sample info file as json. Exiting..")
            click.echo(e)
            sys.exit(-1)
    else:
        click.echo("Could not find supplied sample config. Exiting..")
        sys.exit(-1)
    return data
