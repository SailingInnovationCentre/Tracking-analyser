
"""
Library to visualise data

author: Nerine Usman
created: 09-09-2019
"""

import os, sys ,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from Utilities.converter import *
from Utilities.globalVar import *

class visualise(object):
    def __init__():
        x=3

    def plotWindFreq(windfreq):
        fig = px.line_polar(windfreq, r="Frequency", theta="Wind Direction", color="Wind Speed", line_close=True,
                    color_discrete_sequence=px.colors.sequential.Plasma[-2::-1])
        fig.update_layout( polar = dict(radialaxis = dict(type = "log")))
        return fig
