#!/usr/bin/python
import os

#os.chdir("100_2d");
#os.system("python run_computeenergy.py");
#os.system("python run_faceting.py");
os.chdir("110_2d");
os.system("python run_computeenergy.py");
os.system("python run_faceting.py");
os.chdir("../111_2d");
os.system("python run_computeenergy.py");
os.system("python run_faceting.py");
os.chdir("../112_2d");
os.system("python run_computeenergy.py");
os.system("python run_faceting.py");
print("DONE!");
