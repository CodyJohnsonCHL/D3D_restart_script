#!/usr/bin/env python3

import sys
import os
import shutil
import fileinput
import re
import datetime as dt
from pathlib import Path

# get directories
run_dir = Path.cwd()
model_name = sys.argv[1]
restart_model_name = sys.argv[2]
run_output = run_dir / f'output'
subdomains = int(sys.argv[3])
mapint     = int(sys.argv[4])
tstop      = int(sys.argv[5])
rstint     = int(sys.argv[6])

# timestamp indexes
dt0 = len(model_name) + 6
dtf = dt0 + 8

# get latest restart file
all_timestamps = []
all_restart_files = run_output.glob('*_rst.nc')
for restart_file in all_restart_files:
    timestamp = dt.datetime.strptime(restart_file.stem[dt0:dtf], '%Y%m%d')
    all_timestamps.append(timestamp)

tmax = all_timestamps[0]
for t in all_timestamps[1:]:
    if t > tmax:
        tmax = t

tstr = tmax.strftime('%Y%m%d')

# get tref
orig_mdu = f'{model_name}.mdu'
with open(orig_mdu) as f:
    for line in f:
        if re.search('^RefDate.*', line):
            tref = dt.datetime.strptime(line.split()[2], '%Y%m%d')

# get tstart
tstart = tmax - tref
tstart = int(tstart.total_seconds())

# replace text
text_to_search_1 = r"TStart.*\n"
text_to_search_2 = r"RestartFile.*\n"
text_to_search_3 = r"Tlfsmo.*\n"
text_to_search_4 = r"MapInterval.*\n"
text_to_search_5 = r"ThinDamFile.*\n"
text_to_search_6 = r"CrsFile.*\n"
text_to_search_7 = r"TStop.*\n"
text_to_search_8 = r"RstInterval.*\n"

text_to_replace_1 = f'TStart                            = {tstart}\n'
text_to_replace_3 = f'Tlfsmo                            = 0\n'
text_to_replace_4 = f'MapInterval                       = {mapint}\n'
text_to_replace_5 = f'ThinDamFile                       = main_thd.pli\n'
text_to_replace_6 = f'CrsFile                           = main_refined_crs.pli nested_BCs_crs.pli lower_MS_crs.pli\n'
text_to_replace_7 = f'TStop                             = {tstop}\n'
text_to_replace_8 = f"RstInterval                       = {rstint}\n"

# make changes to original mdu (not sure if this matters)
mdu_path = Path(orig_mdu)
mdu_text = mdu_path.read_text()
mdu_text = re.sub(text_to_search_1, text_to_replace_1, mdu_text)
mdu_text = re.sub(text_to_search_3, text_to_replace_3, mdu_text)
mdu_text = re.sub(text_to_search_4, text_to_replace_4, mdu_text)
mdu_text = re.sub(text_to_search_5, text_to_replace_5, mdu_text)
mdu_text = re.sub(text_to_search_6, text_to_replace_6, mdu_text)
mdu_text = re.sub(text_to_search_7, text_to_replace_7, mdu_text)
mdu_text = re.sub(text_to_search_8, text_to_replace_8, mdu_text)
mdu_path.write_text(mdu_text)

# make changes to partitioned mdus
for n in range(subdomains):
    mdu = f'{model_name}_{n:04d}.mdu'
    restart = run_output.stem + '/'  f'{restart_model_name}_{n:04d}_{tstr}_000000_rst.nc'
    print('working on...')
    print(mdu)
    print(restart)
    print('')
    
    text_to_replace_2 = f'RestartFile                       = {restart}\n'

    mdu_path = Path(mdu)
    mdu_text = mdu_path.read_text()
    mdu_text = re.sub(text_to_search_1, text_to_replace_1, mdu_text)
    mdu_text = re.sub(text_to_search_2, text_to_replace_2, mdu_text)
    mdu_text = re.sub(text_to_search_3, text_to_replace_3, mdu_text)
    mdu_text = re.sub(text_to_search_4, text_to_replace_4, mdu_text)
    mdu_text = re.sub(text_to_search_5, text_to_replace_5, mdu_text)
    mdu_text = re.sub(text_to_search_6, text_to_replace_6, mdu_text)
    mdu_text = re.sub(text_to_search_7, text_to_replace_7, mdu_text)
    mdu_text = re.sub(text_to_search_8, text_to_replace_8, mdu_text)
    mdu_path.write_text(mdu_text)
