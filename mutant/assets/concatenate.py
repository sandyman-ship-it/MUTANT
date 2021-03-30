""" This script concatenates all forward fastq files into one file and
    all reverse fastq files into one file for each sample. The files
    that are used for concatenation will be removed afterwards if they
    got more than 1 inode.
    By: @henningonsbring """

import os
import re
import subprocess
import sys

from datetime import date
from pathlib import Path


if len(sys.argv) > 3 or len(sys.argv) < 2:
    print("Usage: concatenate.py <input_folder> <app_tag> OR concatenate.py <input_folder>")
    sys.exit(-1)

base_path = sys.argv[1]

if len(sys.argv) == 3:
    app_tag = sys.argv[2]

    PREFIX_TO_CONCATENATE = ["MWG", "MWL", "MWM", "MWR", "MWX", "VWG", "VWL", "VWM"]
    should_concatenate = False

    for prefix in PREFIX_TO_CONCATENATE:
        if app_tag.startswith(prefix):
            print("Apptag %s identified, data generated with this application tag should be concatenated" % (app_tag))
            should_concatenate = True

    if should_concatenate == False:
        print("Data with application tag %s should not be concatenated, skipping concatenation" % (app_tag))
        sys.exit(-1)

for dir_name in os.listdir(base_path):
    for read_direction in [1, 2]:
        dir_path = os.path.join(base_path, dir_name)
        if not os.path.isdir(dir_path):
            continue
        same_direction = []
        total_size = 0
        for file in os.listdir(dir_path):
            abs_path_file = os.path.join(dir_path, file)
            direction_string = ".+_R" + str(read_direction) + "_[0-9]+.fastq.gz"
            direction_pattern = re.compile(direction_string)
            if direction_pattern.match(abs_path_file):
                same_direction.append(os.path.abspath(abs_path_file))
                total_size = total_size + Path(abs_path_file).stat().st_size
        same_direction.sort()
        cmd = "cat"
        for i in range(len(same_direction)):
            cmd = cmd + " " + same_direction[i]
        today = date.today()
        today_formatted = today.strftime("%y%m%d")
        output = dir_path + "/" + today_formatted + "_" + dir_name + "_" + str(read_direction) + ".fastq.gz"
        cmd = cmd + " > " + output
        print("Running command: %s" % (cmd))
        os.system(cmd)
        concatenated_size = Path(output).stat().st_size
        if total_size == concatenated_size:
            print("QC PASSED: Total size for files used in concatenation match the size of the concatenated file")
            for file in same_direction:
                inode_check_cmd = "stat -c %h " + file
                n_inodes = subprocess.getoutput(inode_check_cmd)
                if int(n_inodes) > 1:
                    print("Removing file: %s" % (file))
                    os.remove(file)
                else:
                    print("WARNING %s only got 1 inode, file will not be removed" % (file))
        else:
            print("WARNING data lost in concatenation")
