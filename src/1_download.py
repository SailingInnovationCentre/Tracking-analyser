"""
Run to download desired data from SAP server and save in '.\data' folder

author: Nerine Usman
created: 03-09-2019
"""

import os, sys ,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
import numpy as np
import matplotlib.pyplot as plt

import lib.Download.download as download
from Utilities.globalVar import *

### INPUT
eventSelection = Tokyo2019Test
###


for serv in eventSelection:
    download.download(server = serv['name'], \
     regattasContaining = serv['regattaNameContaining']).run(NormalData = True)



print('everything done')
