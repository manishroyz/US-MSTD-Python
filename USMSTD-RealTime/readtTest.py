import tkinter as tk
from random import randint

# these two imports are important
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import time
import threading
import visa
import numpy as np

"""...."""

def plot_waveform(x, y):

    plt.plot(x, y)
    plt.xlabel('i am x label')
    plt.ylabel('i am y label')
    plt.show()
    plt.close()

def data_points():
    filepath = 'ref_data.avg'
    my_list_x = []
    my_list_y = []
    with open(filepath) as ref_data:
        line = ref_data.readline()
        cnt = 1
        while line:
            print("Line {}: {}".format(cnt, line.strip()))
            raw_out = line.strip().split()
            my_list_x.append(raw_out[0])
            my_list_y.append(raw_out[1])
            line = ref_data.readline()
            cnt += 1
    plot_waveform(my_list_x,my_list_y)



data_points()