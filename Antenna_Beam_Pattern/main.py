import numpy as np
import matplotlib.pyplot as plt

theta = np.linspace(-np.pi/2,np.pi/2,1000)
rows = 4
cols = 19
length = 3.8
height = 0.8
pitch_rows = length/cols
pitch_cols = height/rows

f = 9.8e9
c = 3e8
wv = c/f
k = 2*np.pi/wv

w_rows = np.ones(rows)
n = range(rows)
AF = np.sum(w_rows*np.exp(1j*k*n*pitch_rows*np.sin(theta)))

print(AF)