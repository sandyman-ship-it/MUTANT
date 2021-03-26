""" This script concatenates all forward fastq files into one file
    and all reverse fastq files into one file for each sample
    By: @henningonsbring """

import os
import re
import sys

from pathlib import Path


if len(sys.argv) != 3:
    print("Usage: concatenate.py <input_folder> <app_tag>")
    sys.exit(-1)

base_path = sys.argv[1]
app_tag = sys.argv[2]

PREFIX_TO_CONCATENATE = ["MWG", "MWL", "MWM", "MWR", "MWX", "VWG", "VWL", "VWM"]
should_concatenate = False

for prefix in PREFIX_TO_CONCATENATE:
    if app_tag.startswith(prefix):
        print("Apptag " + app_tag + " identified, data generated with this application tag should be concatenated")
        should_concatenate = True

if should_concatenate == False:
    print("Data with application tag " + app_tag + " should not be concatenated, skipping concatenation")
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
        output = dir_path + "/" + dir_name + "_R" + str(read_direction) + ".fastq.gz"
        cmd = cmd + " > " + output
        print("Running command: " + cmd)
        os.system(cmd)
        concatenated_size = Path(output).stat().st_size
        if total_size == concatenated_size:
            print("QC PASSED: Total size for files used in concatenation match the size of the concatenated file")
            for file in same_direction:
                print("Removing file: " + file)
                os.remove(file)
        else:
            print("WARNING data lost in concatenation")