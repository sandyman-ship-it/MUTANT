"""
  By: Isak Sylvin, @sylvinite
"""


import csv
import glob
import os
from datetime import date
from pathlib import Path

import yaml

from mutant.modules.generic_parser import get_sarscov2_config


class DeliverSC2:
    def __init__(self, caseinfo, resdir, config_artic, fastq_dir, timestamp):
        self.casefile = caseinfo
        caseinfo = get_sarscov2_config(caseinfo)

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
        self.fastq_dir = fastq_dir

    def rename_deliverables(self):
        """Rename result files for delivery: fastq, consensus files, vcf and pangolin"""

        for sampleinfo in self.caseinfo:
            sample = sampleinfo["CG_ID_sample"]
            region = sampleinfo["region_code"]
            lab = sampleinfo["lab_code"]
            base_sample = "{0}_{1}_{2}".format(
                region, lab, sampleinfo["Customer_ID_sample"]
            )
            if not sampleinfo["sequencing_qc_pass"]:
                continue

            # rename makeConsensus
            prefix = "{0}/ncovIllumina_sequenceAnalysis_makeConsensus".format(
                self.indir
            )
            for item in glob.glob("{0}/{1}.*".format(prefix, base_sample)):
                newpath = "{0}/{1}.consensus.fasta".format(prefix, base_sample)
                os.symlink(item, newpath)

            # rename typeVariants
            prefix = "{0}/ncovIllumina_Genotyping_typeVariants/vcf".format(self.indir)
            for item in glob.glob("{0}/{1}.csq.vcf".format(prefix, base_sample)):
                newpath = "{0}/{1}.vcf".format(prefix, base_sample)
                os.symlink(item, newpath)

            # rename core
            core_suffix = [
                ".qc.csv",
                ".pangolin.csv",
                ".typing_summary.csv",
                ".variant_summary.csv",
            ]
            for thing in core_suffix:
                hit = glob.glob("{0}/*{1}".format(self.indir, thing))
                if len(hit) == 1:
                    hit = hit[0]
                    os.symlink(hit, "{0}/{1}{2}".format(self.indir, self.ticket, thing))
