""" This class creates reports. Specifically it acts on the sarscov2 pipeline,
    and creates report files for Clinical Genomics Infrastructure

    By: Isak Sylvin & Tanja Normark
"""

import csv
import glob
import os
from datetime import date
from pathlib import Path

import yaml

from mutant.modules.generic_parser import get_sarscov2_config


class ReportSC2:
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


    def create_all_files(self):
        self.create_trailblazer_config()
        self.create_concat_pangolin()
        self.create_deliveryfile()
        self.create_fohm_csv()


    def get_finished_slurm_ids(self) -> list:
        trace_file_path = Path(self.indir, "pipeline_info", "execution_trace.txt")
        slurm_id_list = []
        with open(trace_file_path, "r") as trace_file_contents:
            for line in trace_file_contents:
                slurm_id = line.split()[2]
                try:
                    slurm_id_list.append(int(slurm_id))
                except Exception:
                    continue
        return slurm_id_list

    def create_trailblazer_config(self) -> None:
        trailblazer_config_path = Path(self.indir, "trailblazer_config.yaml")
        finished_slurm_ids = self.get_finished_slurm_ids()
        if not finished_slurm_ids:
            return
        with open(trailblazer_config_path, "w") as trailblazer_config_file:
            yaml.dump(data={"jobs": finished_slurm_ids}, stream=trailblazer_config_file)

    def create_concat_pangolin(self):

        indir = "{0}/ncovIllumina_sequenceAnalysis_pangolinTyping".format(self.indir)

        concat = open("{0}/{1}.pangolin.csv".format(self.indir, self.ticket), "w+")

        for item in glob.glob("{0}/*.csv".format(indir):
                single = open(item, "r")
                concat.write(single.read())
                concat.write("\n")
        concat.close()

    def create_fohm_csv(self):

        """Creates a summary file for FoHM for each region-lab-combination"""

        # Add header to summary files
        for regionlab in self.regionlabs:
            sumfile = os.path.join(
                self.indir,
                "{}_{}_komplettering.csv".format(regionlab, self.today),
            )
            with open(sumfile, "w") as summary:
                summary.write("provnummer,urvalskriterium,GISAID_accession\n")

        # Write sample information to corresponding summary file
        for record in self.caseinfo:
            region = record["region_code"]
            lab = record["lab_code"]
            sumfile = os.path.join(
                self.indir, "{}_{}_{}_komplettering.csv".format(region, lab, self.today)
            )
            with open(sumfile, "a") as out:
                summary = csv.writer(out)
                summary.writerow(
                    [
                        record["Customer_ID_sample"],
                        record["selection_criteria"],
                    ]
                )


    def create_deliveryfile(self):

        """Create deliverables file"""

        deliv = {"files": []}
        delivfile = "{}/{}_deliverables.yaml".format(self.indir, self.case)

        # Project-wide

        # Summary report
        deliv["files"].append(
            {
                "format": "csv",
                "id": self.case,
                "path": "{}/{}.typing_summary.csv".format(self.indir, self.ticket),
                "path_index": "~",
                "step": "report",
                "tag": "SARS-CoV-2-sum",
            }
        )
        # Variant report
        deliv["files"].append(
            {
                "format": "csv",
                "id": self.case,
                "path": "{}/{}.variant_summary.csv".format(self.indir, self.ticket),
                "path_index": "~",
                "step": "report",
                "tag": "SARS-CoV-2-var",
            }
        )
        # QC report
        deliv["files"].append(
            {
                "format": "csv",
                "id": self.case,
                "path": "{}/{}.qc.csv".format(self.indir, self.ticket),
                "path_index": "~",
                "step": "result_aggregation",
                "tag": "SARS-CoV-2-qc",
            }
        )
        # Json (vogue) data
        deliv["files"].append(
            {
                "format": "json",
                "id": self.case,
                "path": "{}/{}.json".format(self.indir, self.case),
                "path_index": "~",
                "step": "result_aggregation",
                "tag": "SARS-CoV-2-json",
            }
        )
        # Sampleinfo/Case
        deliv["files"].append(
            {
                "format": "json",
                "id": self.case,
                "path": "{}".format(self.casefile),
                "path_index": "~",
                "step": "runinfo",
                "tag": "sampleinfo",
            }
        )
        # Settings dump
        deliv["files"].append(
            {
                "format": "txt",
                "id": self.case,
                "path": self.config_artic,
                "path_index": "~",
                "step": "runinfo",
                "tag": "runtime-settings",
            }
        )
        # Execution log
        deliv["files"].append(
            {
                "format": "txt",
                "id": self.case,
                "path": "{}/nextflow.log".format(self.indir),
                "path_index": "~",
                "step": "runinfo",
                "tag": "logfile",
            }
        )

        # Region-lab-wide

        for regionlab in self.regionlabs:
            rl = regionlab
            # Pangolin reports
            deliv["files"].append(
                {
                    "format": "csv",
                    "id": self.case,
                    "path": "{}/ncovIllumina_sequenceAnalysis_makeConsensus/"
                    "{}_{}_pangolin_classification.txt".format(
                        self.indir, rl, self.today
                    ),
                    "path_index": "~",
                    "step": "typing",
                    "tag": "SARS-CoV-2-type",
                }
            )
            # FoHM delivery file
            deliv["files"].append(
                {
                    "format": "csv",
                    "id": self.case,
                    "path": os.path.join(
                        self.indir, "{}_{}_komplettering.csv".format(rl, self.today)
                    ),
                    "path_index": "~",
                    "step": "report",
                    "tag": "SARS-CoV-2-info",
                }
            )

        # Sample-wide

        for record in self.caseinfo:
            sampleID = record["CG_ID_sample"]
            sample = record["Customer_ID_sample"]
            region = record["region_code"]
            lab = record["lab_code"]
            base_sample = "{0}_{1}_{2}".format(region, lab, sample)
            if not record["sequencing_qc_pass"]:
                continue
            # Concat reads forwards
            deliv["files"].append(
                {
                    "format": "fastq",
                    "id": sampleID,
                    "path": "{0}/{1}_1.fastq.gz".format(self.fastq_dir, base_sample),
                    "path_index": "~",
                    "step": "concatination",
                    "tag": "forward-reads",
                }
            )
            # Concat reads reverse
            deliv["files"].append(
                {
                    "format": "fastq",
                    "id": sampleID,
                    "path": "{0}/{1}_2.fastq.gz".format(self.fastq_dir, base_sample),
                    "path_index": "~",
                    "step": "concatination",
                    "tag": "reverse-reads",
                }
            )
            # Consensus files
            deliv["files"].append(
                {
                    "format": "fasta",
                    "id": sampleID,
                    "path": "{}/ncovIllumina_sequenceAnalysis_makeConsensus/{}.consensus.fasta".format(
                        self.indir, base_sample
                    ),
                    "path_index": "~",
                    "step": "consensus",
                    "tag": "consensus",
                }
            )
            # Alignment (bam, sorted)
            deliv["files"].append(
                {
                    "format": "bam",
                    "id": sampleID,
                    "path": "{}/ncovIllumina_sequenceAnalysis_readMapping/{}.sorted.bam".format(
                        self.indir, base_sample
                    ),
                    "path_index": "~",
                    "step": "alignment",
                    "tag": "reference-alignment-sorted",
                }
            )
            # Variants (csq-vcf)
            deliv["files"].append(
                {
                    "format": "vcf",
                    "id": sampleID,
                    "path": "{}/ncovIllumina_Genotyping_typeVariants/vcf/{}.vcf".format(
                        self.indir, base_sample
                    ),
                    "path_index": "~",
                    "step": "genotyping",
                    "tag": "variants",
                }
            )
            # Variants (tsv)
            deliv["files"].append(
                {
                    "format": "tsv",
                    "id": sampleID,
                    "path": "{}/ncovIllumina_sequenceAnalysis_callVariants/{}.variants.tsv".format(
                        self.indir, base_sample
                    ),
                    "path_index": "~",
                    "step": "variant-calling",
                    "tag": "variants",
                }
            )
        with open(delivfile, "w") as out:
            yaml.dump(deliv, out)
