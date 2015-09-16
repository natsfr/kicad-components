import sys
import os

from odb_data import *

from pcbnew import *

odb_name = sys.argv[1]
step_name = sys.argv[2]
brd_name = sys.argv[3]

board = LoadBoard(brd_name)

plot_dir = "%s\/" % odb_name
odb_dir_root = plot_dir+"\/steps\/"+step_name

# Generate EDA data
#if(not os.path.exists(odb_dir_root + "\/eda\/")):
	#print "Bad file tree\n"
	#exit()

#if(not os.path.exists(odb_dir_root + "\/eda\/")):
	#print "Bad file tree\n"
	#exit()

#s_data = gen_data_file(board);
odb_instance = ODB_GEN()
odb_instance.gen_comp_file(board)
