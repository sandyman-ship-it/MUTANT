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

from mutant.modules.generic_parser import get_sarscov2_config, get_json


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
        self.articdata = dict()

    def create_all_files(self):
        self.create_trailblazer_config()
        self.create_concat_pangolin()
        self.create_concat_consensus()
        self.create_deliveryfile()
        self.create_fohm_csv()
        self.create_sarscov2_resultfile()
        self.create_sarscov2_variantfile()
        self.create_jsonfile()

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

        for item in glob.glob("{0}/*.csv".format(indir)):
            single = open(item, "r")
            concat.write(single.read())
            concat.write("\n")
        concat.close()

    def create_concat_consensus(self):

        indir = "{0}/ncovIllumina_sequenceAnalysis_makeConsensus".format(self.indir)

        concat = open("{0}/{1}.consensus.fa".format(self.indir, self.ticket), "w+")

        for item in glob.glob("{0}/*.consensus.fa".format(indir)):
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

    def create_sarscov2_resultfile(self):
        """Write summary csv report of Artic and Pangolin results"""

        ticket = self.ticket
        today = self.today
        results = self.articdata

        summaryfile = os.path.join(
            indir, "sars-cov-2_{}_results_{}.csv".format(ticket, today)
        )
        with open(summaryfile, mode="w") as out:
            summary = csv.writer(out)
            summary.writerow(
                [
                    "Sample",
                    "Selection",
                    "Ticket",
                    "%N_bases",
                    "%10X_coverage",
                    "QC_pass",
                    "Lineage",
                    "PangoLEARN_version",
                    "VOC",
                    "Variants",
                ]
            )
            for sample, data in results.items():
                selection = "-"
                row = [
                    sample,
                    selection,
                    ticket,
                    data["pct_n_bases"],
                    data["pct_10X_bases"],
                    data["qc"],
                    data["lineage"],
                    data["pangoLEARN_version"],
                    data["VOC"],
                    data["VOC_aa"],
                ]
                summary.writerow(row)

    def create_sarscov2_variantfile(self):
        """Write variant csv report of identified variants
        I am literally just variant_summary.csv but with sample names"""

        indir = self.indir
        ticket = self.ticket
        today = self.today

        varRep = glob.glob(os.path.join(indir, "*variant_summary.csv"))[0]
        varout = os.path.join(
            indir, "sars-cov-2_{}_variants_{}.csv".format(ticket, today)
        )
        if os.stat(varRep).st_size != 0:
            with open(varRep) as f, open(varout, mode="w") as out:
                variants = f.readlines()
                varsummary = csv.writer(out)
                varsummary.writerow(variants[0].strip().split(","))
                for line in variants[1:]:
                    line = line.strip().split(",")
                    varsummary.writerow([line[0].split("_")[-1]] + line[1:])
        else:
            try:
                open(varout, "a").close()
            except Exception as e:
                print("Failed creating file {}\n{}".format(varout, e))

    def create_jsonfile(self):

        """Output all result data in a json format for easy parsing"""

        with open(
            "{}/{}_{}".format(self.indir, self.ticket, self.today), "w"
        ) as outfile:
            json.dump(self.articdata, outfile)

    def parse_artic_csv(self):
        """Parse artic output directory for analysis results. Returns dictionary data object"""
        indir = self.indir
        voc_pos = range(475, 486)
        voc_pos_aa = ["L452R"]
        voc_strains = get_json(
            "{0}/voc_strains.json".format(os.path.dirname(os.path.realpath(__file__)))
        )

        artic_data = dict()
        var_all = dict()
        var_voc = dict()

        # Files of interest. ONLY ADD TO END OF THIS LIST
        files = [
            "*qc.csv",
            "*variant_summary.csv",
            "ncovIllumina_sequenceAnalysis_makeConsensus/*pangolin.csv",
        ]
        paths = list()
        for f in files:
            try:
                hits = glob.glob(os.path.join(indir, f))
                if len(hits) == 0:
                    raise Exception("File not found")
                if len(hits) > 1:
                    print(
                        "Multiple hits for {0}/{1}, picking {2}".format(
                            indir, f, hits[0]
                        )
                    )
                paths.append(hits[0])
            except Exception as e:
                print("Unable to find {0} in {1} ({2})".format(f, indir, e))
                sys.exit(-1)

        # Parse qc report data
        with open(paths[0]) as f:
            content = csv.reader(f)
            next(content)
            for line in content:
                sample = line[0].split("_")[-1]
                if float(line[2]) > 95:
                    passed = "TRUE"
                else:
                    passed = "FALSE"
                artic_data[sample] = {
                    "pct_n_bases": line[1],
                    "pct_10X_bases": line[2],
                    "longest_no_N_run": line[3],
                    "num_aligned_reads": line[4],
                    "artic_qc": line[7],
                    "qc": passed,
                }
        # Parse Pangolin report data
        with open(paths[2]) as f:
            content = csv.reader(f)
            next(content)
            for line in content:
                sample = line[0].split(".")[0].split("_")[-1]
                lineage = line[1]
                if lineage in voc_strains:
                    voc = "Yes"
                elif lineage == "None":
                    voc = "-"
                else:
                    voc = "No"
                artic_data[sample].update(
                    {
                        "lineage": lineage,
                        "pangolin_probability": line[2],
                        "pangoLEARN_version": line[3],
                        "pangolin_qc": line[4],
                        "VOC": voc,
                    }
                )
        # Parse Variant report data
        if os.stat(paths[1]).st_size != 0:
            with open(paths[1]) as f:
                content = csv.reader(f)
                next(content)
                for line in content:
                    sample = line[0].split("_")[-1]
                    variant = line[2]
                    pos = int(re.findall(r"\d+", variant)[0])
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
                    if len(var_all[sample]) > 1:
                        artic_data[sample].update(
                            {"variants": ";".join(var_all[sample])}
                        )
                    else:
                        artic_data[sample].update({"variants": var_all[sample]})
                else:
                    artic_data[sample].update({"variants": "-"})
        self.artic_data = artic_data

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
