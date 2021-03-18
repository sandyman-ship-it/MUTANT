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
from mutant.assets.run.run_artic import RunSC2

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
@click.option("--config_artic", help="Custom artic configuration file", default="{}/config/hasta/artic.json".format(WD))
@click.option("--config_case", help="Provided config for the case", default="")
@click.option("--config", help="General configuration file for MUTANT", default="")
@click.option("--outdir", help="Output folder to override general configutations", default="")
@click.option("--profiles", help="Execution profiles, comma-separated", default="singularity,slurm")
@click.pass_context
def sarscov2(ctx, input_folder, config_artic, config_case, config, outdir, profiles):

    # Set base for output files
    if config_case != "":
        caseinfo = get_json_data(config_case)
        caseID = caseinfo[0]["case_ID"]
    else:
        caseID = "artic"
    prefix = "{}_{}".format(caseID, TIMESTAMP)

    # Run
    run = RunSC2(
        input_folder=input_folder,
        config_artic=config_artic,
        caseID=caseID,
        prefix=prefix,
        profiles=profiles,
        timestamp=TIMESTAMP,
        WD=WD
    )
    resdir = run.get_results_dir(config, outdir)
    run.run_case(resdir)

    # Deliverables
    if config_case != "":
        delivery = DeliverSC2(
            caseinfo=caseinfo,
            resdir=os.path.abspath(resdir),
            config_artic=config_artic,
            timestamp=TIMESTAMP
        )
        delivery.rename_deliverables()
        delivery.gen_delivery(prefix)
        delivery.create_fohm_csv()

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

def get_json_data(config):
    if os.path.exists(config):
        """Get sample information as json object"""
        try:
            with open(config) as json_file:
                data = json.load(json_file)
        except Exception as e:
            click.echo("Unable to read provided json file: {}. Exiting..".format(config))
            click.echo(e)
            sys.exit(-1)
    else:
        click.echo("Could not find supplied config: {}. Exiting..".format(config))
        sys.exit(-1)
    return data
