import sys
import os

from odb_data import gen_data_file

from pcbnew import *
odb_name = sys.argv[1]
brd_name = sys.argv[2]

board = LoadBoard(brd_name)

plot_dir = "%s\/" % odb_name
odb_dir_root = plot_dir+"\/steps\/"+odb_name

if (not os.path.exists(plot_dir)):
	os.makedirs(odb_dir_root)

# Generate EDA data
if(not os.path.exists(odb_dir_root + "\/eda\/")):
	os.makedirs(odb_dir_root + "eda")

s_data = gen_data_file(board);