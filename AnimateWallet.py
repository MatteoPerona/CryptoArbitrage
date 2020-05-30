import pandas as pd
import csv

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from datetime import datetime
import time

def animate(i):
    data = pd.read_csv('wallet.csv')
    #x = data['Time']
    y = data['Cash']

    plt.cla()

    #plt.plot(x, y, label='$')
    plt.plot(y, label='$')

    plt.legend(loc='upper left')
    plt.tight_layout()

if __name__ == "__main__":
    ain = FuncAnimation(plt.gcf(), animate)
    plt.show()

