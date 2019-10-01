
"""
Run to  transform raw data from multiple races to 20 different pandas databases.
Saves them as sql databases in local data base

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
import lib.TransformData.combineData as comb
import lib.SQLlib.sql as sql
from Utilities.globalVar import *

### INPUT
eventSelection = Tokyo2019Test
filenames = ['regattas',
             # 'races',
             # 'windsummary',
             # 'course',
             # 'races/entries',
             # 'firstlegbearing',
             # 'markpassings',
             # 'targettime',
             # 'times',
             # 'wind',
             # 'legs',
             # 'live',
             # 'competitor_positions',
             # 'marks_positions',
             # 'maneuvers',
             # 'datamining', ## multiple
             # 'entries',
             ]
###

c = comb.combineData()
dataframes = c.combineFiles(filenames = AllFilenames)
s = sql.sql()
s.saveDataframes(dataframes)


print('everything done')
