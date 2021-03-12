""" This script creates a custom report from the QC output of the ARTIC pipeline,
    applied on SARS-CoV-2 samples 
    By: @talnor """
import os
import sys
import glob
from datetime import date
import csv
import re
import json

if len(sys.argv) != 3:
    sys.exit(-1)

indir = sys.argv[1]
ticket = sys.argv[2]
voc_strain = ["A.23.1", "A.27", "A.28",
              "B.1.1.7", "B.1.351", "B.1.525", "B.1.526", "B.1.1.318", "B.1.427", "B.1.429",
              "C.16", "P.1", "P.2", "R.1", "R.2"]
voc_pos = range(475, 486)
voc_pos_aa = ["L452R"]
today = date.today().strftime("%Y%m%d")

def append_dict(dictionary, key, item):
    if key in dictionary.keys():
        dictionary[key].append(item)
    else:
        dictionary[key] = [item]
    return dictionary

def get_results(indir, voc_strain, voc_pos, voc_pos_aa):

    """ Parse output directory for analysis results. Return dictionary data object """

    artic_data = dict()
    var_all = dict()
    var_voc = dict()

    # Get result files
    qcRep = glob.glob(os.path.join(indir, "*qc.csv"))[0]
    varRep = glob.glob(os.path.join(indir, "*variant_summary.csv"))[0]
    pangolinRep = glob.glob(os.path.join(indir, "ncovIllumina_sequenceAnalysis_makeConsensus/*pangolin.csv"))[0]

    # Parse qc report data
    with open(qcRep) as f:
        content = csv.reader(f)
        next(content)
        for line in content:
            #sample = line[0].split("_")[2]
            sample = line[0]        ####TEMPSTUFF
            if float(line[2]) > 95:
                passed = "TRUE"
            else:
                passed = "FALSE"
            artic_data[sample] = {"pct_n_bases": line[1], "pct_10X_bases": line[2], "longest_no_N_run": line[3],
                                  "num_aligned_reads": line[4], "artic_qc": line[7], "qc": passed}
    # Parse Pangolin report data
    with open(pangolinRep) as f:
        content = csv.reader(f)
        next(content)
        for line in content:
            #sample = line[0].split("_")[3].split(".")[0]
            sample = line[0].split("_")[1].split(".")[0]        ####TEMPSTUFF
            lineage = line[1]
            if lineage in voc_strain:
                voc = "Yes"
            elif lineage == "None":
                voc = "-"
            else:
                voc = "No"
            artic_data[sample].update({"lineage": lineage, "pangolin_probability": line[2],
                                       "pangoLEARN_version": line[3], "pangolin_qc": line[4], "VOC": voc})
    # Parse Variant report data
    if os.stat(varRep).st_size != 0:
        with open(varRep) as f:
            content = csv.reader(f)
            next(content)
            for line in content:
                sample = line[0].split("_")[2]
                variant = line[2]
                pos = int(re.findall(r'\d+', variant)[0])
                if (pos in voc_pos) or (variant in voc_pos_aa):
                    append_dict(var_voc, sample, variant)
                append_dict(var_all, sample, variant)

    # Add variant data to results
    if var_voc:
        for sample in artic_data.keys():
            if sample in var_voc.keys():
                artic_data[sample].update({"VOC_aa": ";".join(var_voc[sample])})
            else:
                artic_data[sample].update({"VOC_aa": "-"})
    else:
        for sample in artic_data.keys():
            artic_data[sample].update({"VOC_aa": "-"})
    if var_all:
        for sample in artic_data.keys():
            if sample in var_all.keys():
                artic_data[sample].update({"variants": ";".join([var_all[sample]])})
            else:
                artic_data[sample].update({"variants": "-"})
    return artic_data

def write_summary_report(results, ticket, today):

    """Write summary csv report of Artic and Pangolin results"""

    summaryfile = os.path.join(indir, "sars-cov-2_{}_results_{}.csv".format(ticket, today))
    with open(summaryfile, mode='w') as out:
        summary = csv.writer(out)
        summary.writerow(["Sample", "Selection", "Ticket", "%N_bases", "%Covered_bases", "QC_pass", "Lineage",
                          "PangoLEARN_version", "VOC", "Variants"])
        for sample, data in results.items():
            selection = "-"
            row = [sample, selection, ticket, data["pct_n_bases"], data["pct_10X_bases"], data["qc"],
                            data["lineage"], data["pangoLEARN_version"], data["VOC"], data["VOC_aa"]]
            summary.writerow(row)

def write_variant_report(indir, ticket, today):

    """Write variant csv report of identified variants"""

    varRep = glob.glob(os.path.join(indir, "*variant_summary.csv"))[0]
    varout = os.path.join(indir, "sars-cov-2_{}_variants_{}.csv".format(ticket, today))
    if os.stat(varRep).st_size != 0:
        with open(varRep) as f, open(varout, mode='w') as out:
            variants = f.readlines()
            varsummary = csv.writer(out)
            varsummary.writerow(variants[0].strip().split(","))
            for line in variants[1:]:
                line = line.strip().split(",")
                varsummary.writerow([line[0].split("_")[2]] + line[1:])
    else:
        try:
            open(varout, 'a').close()
        except Exception as e:
            print('Failed creating file {}\n{}'.format(varout, e))

def json_dump(data, jsonfile):

    with open(jsonfile, "w") as outfile:
        json.dump(data, outfile)

# Create result summaries
results = get_results(indir, voc_strain, voc_pos, voc_pos_aa)
write_summary_report(results, ticket, today)
write_variant_report(indir, ticket, today)
json_dump(results, "{}_{}.json".format(ticket, today))
