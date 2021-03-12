""" This script renames the output files for the ARTIC pipeline and Pangolin analysis,
    and creates a deliverables file for Clinical Genomics Infrastructure"""
import os
import sys
import glob
from datetime import date
import yaml


class DeliverSC2:


    def __init__(self, caseinfo, resdir, TIMESTAMP):
        self.caseinfo = caseinfo
        self.case = caseinfo[0]["case_ID"]
        self.ticket = caseinfo[0]["Customer_ID_project"]
        self.project = caseinfo[0]["Customer_ID_project"]
        self.region_code = caseinfo[0]["region_code"]
        self.lab_code = caseinfo[0]["lab_code"]
        self.indir = resdir
        self.time = TIMESTAMP
        today = date.today().strftime("%Y%m%d")
        self.today = today

    def rename_deliverables(self):

        """Rename result files for delivery: fastq, consensus files, vcf and pangolin"""

        base = "{}_{}".format(self.region_code, self.lab_code)
        for sampleinfo in self.caseinfo:
            sample = sampleinfo["Customer_ID_sample"]
            # Fastq renaming
            # Consensus renaming
            fasta = glob.glob(os.path.join(self.indir,
                     "ncovIllumina_sequenceAnalysis_makeConsensus/{}.primertrimmed.consensus.fa".format(sample)))[0]
            new_fasta = os.path.join(os.path.dirname(fasta), "{}_{}.consensus.fasta".format(base, sample))
            os.rename(fasta, new_fasta)
            # Rename VCF
            vcf = glob.glob(os.path.join(self.indir,
                                         "ncovIllumina_Genotyping_typeVariants/vcf/{}.csq.vcf".format(sample)))[0]
            new_vcf = os.path.join(os.path.dirname(vcf), "{}_{}.vcf".format(base, sample))
            os.rename(vcf, new_vcf)
        # Pangolin renaming
        #pangolinRep = glob.glob(os.path.join(self.indir,
        #                                     "ncovIllumina_sequenceAnalysis_makeConsensus/*pangolin.csv"))[0]
        #new_pangolin = os.path.join(os.path.dirname(pangolinRep),
        #                            "{}_{}_pangolin_classification.txt".format(base, self.today))
        #os.rename(pangolinRep, new_pangolin)

    def gen_delivery(self, prefix):

        """Create deliverables file"""

        deliv = dict()
        deliv['files'] = list()
        output = "{}/{}_deliverables.yaml".format(self.indir, self.case)
        base = "{}_{}".format(self.region_code, self.lab_code)

        # Project-wide
        # Sampleinfo
        deliv['files'].append({'format': 'json', 'id': self.case,
                               'path': "{}/{}_sampleinfo.json".format(self.indir, self.case),
                               'path_index': '~', 'step': 'analysis', 'tag': 'sampleinfo'})
        # QC report
        deliv['files'].append({'format': 'csv', 'id': self.case,
                               'path': "{}/{}.qc.csv".format(self.indir, prefix),
                               'path_index': '~', 'step': 'result_aggregation', 'tag': 'SARS-CoV-2'})
        # Summary report
        deliv['files'].append({'format': 'csv', 'id': self.case,
                               'path': "{}/sars-cov-2_{}_results_{}.csv".format(self.indir, self.ticket, self.today),
                               'path_index': '~', 'step': 'result_aggregation', 'tag': 'SARS-CoV-2'})
        # Variant report
        deliv['files'].append({'format': 'csv', 'id': self.case,
                               'path': "{}/sars-cov-2_{}_variants_{}.csv".format(self.indir, self.ticket, self.today),
                               'path_index': '~', 'step': 'result_aggregation', 'tag': 'SARS-CoV-2'})
        # Pangolin report
        deliv['files'].append({'format': 'csv', 'id': self.case,
                               'path': "{}/ncovIllumina_sequenceAnalysis_makeConsensus/{}_{}_pangolin_classification.txt"
                                .format(self.indir, base, self.today),
                               'path_index': '~', 'step': 'result_aggregation', 'tag': 'SARS-CoV-2'})
        # Json (vogue) report
        deliv['files'].append({'format': 'json', 'id': self.case,
                               'path': "{}/{}.json".format(self.indir, self.case),
                               'path_index': '~', 'step': 'result_aggregation', 'tag': 'SARS-CoV-2-json'})
        # Settings dump
        #deliv['files'].append({'format': 'txt', 'id': self.case,
        #                       'path': "{}/config.log".format(self.indir),
        #                       'path_index': '~', 'step': 'analysis', 'tag': 'runtime-settings'})

        # Sample-wide
        for record in self.caseinfo:
            sampleID = record["CG_ID_sample"]
            sample = record["Customer_ID_sample"]
            base_sample = "{}_{}".format(base, sampleID)
            # Consensus file
            deliv['files'].append({'format': 'fasta', 'id': sampleID,
                                   'path': "{}/ncovIllumina_sequenceAnalysis_makeConsensus/{}.consensus.fasta"
                                   .format(self.indir, base_sample),
                                   'path_index': '~', 'step': 'consensus', 'tag': 'consensus'})
            # Nextflow log dump/slurm dump
            # Alignment (bam, sorted)
            deliv['files'].append({'format': 'bam', 'id': sampleID,
                                   'path': "{}/ncovIllumina_sequenceAnalysis_readMapping/{}.sorted.bam".format(
                                       self.indir, sample),
                                   'path_index': '~', 'step': 'alignment', 'tag': 'reference-alignment-sorted'})
            # Variants (csq-vcf)
            deliv['files'].append({'format': 'vcf', 'id': sampleID,
                                   'path': "{}/ncovIllumina_Genotyping_typeVariants/vcf/{}.vcf".format(self.indir,
                                                                                                           base_sample),
                                   'path_index': '~', 'step': 'variant-calling', 'tag': 'vcf'})
        with open(output, 'w') as delivfile:
            yaml.dump(deliv, delivfile)