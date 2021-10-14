#!/usr/bin/env python3

import argparse
import datetime as dt
import re
import shutil
from pathlib import Path

# argument parser
parser = argparse.ArgumentParser(description="Script to set up delft3d model restart")

parser.add_argument("mdu", type=Path, help="master mdu filename")

parser.add_argument("tstop", help="datetime to stop restarted model run (YYYY-MM-DD)")

parser.add_argument(
    "--run_output",
    default="./output",
    type=Path,
    help="directory containing restart files (defult = output)",
    dest="run_output",
)

parser.add_argument(
    "--store_prev",
    default="./output_prev",
    type=Path,
    help="directory name to store previous run's output",
    dest="store_prev",
)

parser.add_argument(
    "--mapint", type=int, help="Map output interval (mapint) in seconds", dest="mapint"
)

parser.add_argument(
    "--rstint",
    type=int,
    help="restart file interval (rstint) in seconds",
    dest="rstint",
)

args = parser.parse_args()

mdu = args.mdu
run_output = args.run_output
store_prev = args.store_prev
tstop = args.tstop

mapint = args.mapint
rstint = args.rstint

# move output dirs
# shutil.move(run_output, store_prev)

# get run specific info
run_dir = Path.cwd()
model_name = mdu.stem
subdomains = len(list(run_dir.glob(f"{model_name}_*.mdu")))

# timestamp indexes
dt0 = len(model_name) + 6
dtf = dt0 + 8

# get latest restart file
all_timestamps = []
all_restart_files = run_output.glob(f"{model_name}_*_rst.nc")
for restart_file in all_restart_files:
    timestamp = dt.datetime.strptime(restart_file.stem[dt0:dtf], "%Y%m%d")
    all_timestamps.append(timestamp)

tmax = all_timestamps[0]
for t in all_timestamps[1:]:
    if t > tmax:
        tmax = t

tstr = tmax.strftime("%Y%m%d")

# get tref
orig_mdu = f"{model_name}.mdu"
with open(orig_mdu) as f:
    for line in f:
        if re.search("^RefDate.*", line):
            tref = dt.datetime.strptime(line.split()[2], "%Y%m%d")


# get tstart
tstart = tmax - tref
tstart = int(tstart.total_seconds())


# get tstop
tstop = dt.datetime.strptime(tstop, "%Y-%m-%d")
tstop = tstop - tref
tstop = int(tstop.total_seconds())


# replace text
text_to_search_1 = r"TStart.*\n"
text_to_search_2 = r"RestartFile.*\n"
text_to_search_3 = r"Tlfsmo.*\n"
text_to_search_4 = r"TStop.*\n"

text_to_replace_1 = f"TStart                            = {tstart}\n"
text_to_replace_3 = f"Tlfsmo                            = 0\n"
text_to_replace_4 = f"TStop                             = {tstop}\n"

text_to_search_5 = r"MapInterval.*\n"
text_to_search_6 = r"RstInterval.*\n"

text_to_replace_5 = f"MapInterval                       = {mapint}\n"
text_to_replace_6 = f"RstInterval                       = {rstint}\n"

# make changes to original mdu (not sure if this matters)
mdu_path = Path(orig_mdu)
mdu_text = mdu_path.read_text()
mdu_text = re.sub(text_to_search_1, text_to_replace_1, mdu_text)
mdu_text = re.sub(text_to_search_3, text_to_replace_3, mdu_text)
mdu_text = re.sub(text_to_search_4, text_to_replace_4, mdu_text)

if mapint:
    mdu_text = re.sub(text_to_search_5, text_to_replace_5, mdu_text)

if rstint:
    mdu_text = re.sub(text_to_search_6, text_to_replace_6, mdu_text)

mdu_path.write_text(mdu_text)

# make changes to partitioned mdus
for n in range(subdomains):
    mdu = f"{model_name}_{n:04d}.mdu"
    restart = run_output.stem + "/" f"{model_name}_{n:04d}_{tstr}_000000_rst.nc"
    print("working on...")
    print(mdu)
    print(restart)
    print("")

    text_to_replace_2 = f"RestartFile                       = {restart}\n"

    mdu_path = Path(mdu)
    mdu_text = mdu_path.read_text()
    mdu_text = re.sub(text_to_search_1, text_to_replace_1, mdu_text)
    mdu_text = re.sub(text_to_search_2, text_to_replace_2, mdu_text)
    mdu_text = re.sub(text_to_search_3, text_to_replace_3, mdu_text)
    mdu_text = re.sub(text_to_search_4, text_to_replace_4, mdu_text)

    if mapint:
        mdu_text = re.sub(text_to_search_5, text_to_replace_5, mdu_text)
    if rstint:
        mdu_text = re.sub(text_to_search_6, text_to_replace_6, mdu_text)

    mdu_path.write_text(mdu_text)
