""" This script renames the output files for the ARTIC pipeline and Pangolin analysis,
    and creates a deliverables file for Clinical Genomics Infrastructure"""

import glob
import os
from datetime import date
import yaml
import csv


class DeliverSC2:

    def __init__(self, caseinfo, resdir, config_artic, timestamp):

        regionlab_list = []
        for record in caseinfo:
            regionlab = "{}_{}".format(record["region_code"], record["lab_code"])
            if regionlab not in regionlab_list:
                regionlab_list.append(regionlab)
        self.caseinfo = caseinfo
        self.case = caseinfo[0]["case_ID"]
        self.ticket = caseinfo[0]["Customer_ID_project"]
        self.project = caseinfo[0]["Customer_ID_project"]
        self.regionlabs = regionlab_list
        self.indir = resdir
        self.config_artic = config_artic
        self.time = timestamp
        today = date.today().strftime("%Y%m%d")
        self.today = today

    def rename_deliverables(self):
        """Rename result files for delivery: fastq, consensus files, vcf and pangolin"""

        prefix_fa = "{0}/ncovIllumina_sequenceAnalysis_makeConsensus".format(self.indir)
        prefix_vcf = "{0}/ncovIllumina_Genotyping_typeVariants/vcf".format(self.indir)

        for sampleinfo in self.caseinfo:
            sample = sampleinfo["CG_ID_sample"]
            region = sampleinfo["region_code"].replace(' ', '_')
            lab = sampleinfo["lab_code"].replace(' ', '_')

            #This will only resolve once
            for item in glob.glob("{0}/*{1}*".format(prefix_fa, sample)):
                orgpath = "{1}".format(prefix_fa, item)
                newpath = "{0}/{1}_{2}_{3}.consensus.fasta".format(prefix_fa, region, lab, sampleinfo["Customer_ID_sample"])
                os.rename(orgpath, newpath)

            #This will only resolve once
            for item in glob.glob("{0}/*{1}*.csq.vcf".format(prefix_vcf, sample)):
                orgpath = "{1}".format(prefix_vcf, item)
                newpath = "{0}/{1}_{2}_{3}.vcf".format(prefix_vcf, region, lab, sampleinfo["Customer_ID_sample"])
                os.rename(orgpath, newpath)
           
            # Pangolin renaming
            # pangolinRep = glob.glob(os.path.join(self.indir,
            #                                     "ncovIllumina_sequenceAnalysis_makeConsensus/*pangolin.csv"))[0]
            # new_pangolin = os.path.join(os.path.dirname(pangolinRep),
            #                            "{}_{}_pangolin_classification.txt".format(base, self.today))
            # os.rename(pangolinRep, new_pangolin)

    def gen_delivery(self, prefix):

        """Create deliverables file"""

        deliv = dict()
        deliv['files'] = list()
        delivfile = "{}/{}_deliverables.yaml".format(self.indir, self.case)

        # Project-wide

        # Summary report
        deliv['files'].append({'format': 'csv', 'id': self.case,
                               'path': "{}/sars-cov-2_{}_results_{}.csv".format(self.indir, self.ticket, self.today),
                               'path_index': '~', 'step': 'report', 'tag': 'SARS-CoV-2-sum'})
        # Variant report
        deliv['files'].append({'format': 'csv', 'id': self.case,
                               'path': "{}/sars-cov-2_{}_variants_{}.csv".format(self.indir, self.ticket, self.today),
                               'path_index': '~', 'step': 'report', 'tag': 'SARS-CoV-2-var'})
        # QC report
        deliv['files'].append({'format': 'csv', 'id': self.case,
                               'path': "{}/{}.qc.csv".format(self.indir, prefix),
                               'path_index': '~', 'step': 'result_aggregation', 'tag': 'SARS-CoV-2-qc'})
        # Json (vogue) data
        deliv['files'].append({'format': 'json', 'id': self.case,
                               'path': "{}/{}.json".format(self.indir, self.case),
                               'path_index': '~', 'step': 'result_aggregation', 'tag': 'SARS-CoV-2-json'})
        # Sampleinfo
        deliv['files'].append({'format': 'json', 'id': self.case,
                               'path': "{}/{}_sampleinfo.json".format(self.indir, self.case),
                               'path_index': '~', 'step': 'runinfo', 'tag': 'sampleinfo'})
        # Settings dump
        deliv['files'].append({'format': 'txt', 'id': self.case,
                               'path': self.config_artic,
                               'path_index': '~', 'step': 'runinfo', 'tag': 'runtime-settings'})
        # Execution log
        deliv['files'].append({'format': 'txt', 'id': self.case,
                               'path': "{}/nextflow.log".format(self.indir),
                               'path_index': '~', 'step': 'runinfo', 'tag': 'logfile'})

        # Region-lab-wide

        for regionlab in self.regionlabs:
            rl = regionlab.replace(' ', "_")
            # Pangolin reports
            deliv['files'].append({'format': 'csv', 'id': self.case,
                                   'path': "{}/ncovIllumina_sequenceAnalysis_makeConsensus/"
                                           "{}_{}_pangolin_classification.txt".format(self.indir, rl,
                                                                                      self.today),
                                   'path_index': '~', 'step': 'typing', 'tag': 'SARS-CoV-2-type'})
            # FoHM delivery file
            deliv['files'].append({'format': 'csv', 'id': self.case,
                                   'path': os.path.join(self.indir,
                                                        "{}_{}_komplettering.csv".format(rl, self.today)),
                                   'path_index': '~', 'step': 'report', 'tag': 'SARS-CoV-2-info'})

        # Sample-wide

        for record in self.caseinfo:
            sampleID = record["CG_ID_sample"]
            sample = record["Customer_ID_sample"]
            region = record["region_code"].replace(' ', '_')
            lab = record["lab_code"].replace(' ', '_')
            base = "{}_{}".format(region, lab)
            base_sample = "{}_{}".format(base, sampleID)
            # Concat reads forwards
            deliv['files'].append({'format': 'fastq', 'id': sampleID,
                                   'path': "{0}/concat/{1}_1.fastq.gz".format(self.indir, base_sample),
                                   'path_index': '~', 'step': 'concatination', 'tag': 'forward-reads'})
            # Concat reads reverse
            deliv['files'].append({'format': 'fastq', 'id': sampleID,
                                   'path': "{0}/concat/{1}_2.fastq.gz".format(self.indir, base_sample),
                                   'path_index': '~', 'step': 'concatination', 'tag': 'reverse-reads'})
            # Consensus file
            deliv['files'].append({'format': 'fasta', 'id': sampleID,
                                   'path': "{}/ncovIllumina_sequenceAnalysis_makeConsensus/{}.consensus.fasta"
                                   .format(self.indir, base_sample),
                                   'path_index': '~', 'step': 'consensus', 'tag': 'consensus'})
            # Alignment (bam, sorted)
            deliv['files'].append({'format': 'bam', 'id': sampleID,
                                   'path': "{}/ncovIllumina_sequenceAnalysis_readMapping/{}.sorted.bam".format(
                                       self.indir, sample),
                                   'path_index': '~', 'step': 'alignment', 'tag': 'reference-alignment-sorted'})
            # Variants (csq-vcf)
            deliv['files'].append({'format': 'vcf', 'id': sampleID,
                                   'path': "{}/ncovIllumina_Genotyping_typeVariants/vcf/{}.vcf".format(self.indir,
                                                                                                       base_sample),
                                   'path_index': '~', 'step': 'genotyping', 'tag': 'variants'})
            # Variants (tsv)
            deliv['files'].append({'format': 'tsv', 'id': sampleID,
                                   'path': "{}/ncovIllumina_sequenceAnalysis_callVariants/{}.variants.tsv".format(
                                       self.indir, base_sample),
                                   'path_index': '~', 'step': 'variant-calling', 'tag': 'variants'})
        with open(delivfile, 'w') as out:
            yaml.dump(deliv, out)

    def create_fohm_csv(self):

        """Creates a summary file for FoHM for each region-lab-combination"""

        # Add header to summary files
        for regionlab in self.regionlabs:
            sumfile = os.path.join(self.indir, "{}_{}_komplettering.csv".format(regionlab, self.today))
            with open(sumfile, "w") as summary:
                summary.write("provnummer,urvalskriterium,GISAID_accession\n")
        # Write sample information to corresponding summary file
        for record in self.caseinfo:
            sumfile = os.path.join(self.indir, "{}_{}_{}_komplettering.csv".format(record["region_code"],
                                                                                   record["lab_code"], self.today))
            with open(sumfile, "a") as out:
                summary = csv.writer(out)
                summary.writerow([record["Customer_ID_sample"], record["selection_criteria"].split(".")[1].strip()])
