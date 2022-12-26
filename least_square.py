#!/usr/bin/python3

import numpy as np
from numpy.linalg import inv
import matplotlib.pyplot as plt

# Generate our data
n = 200
vals = 10
noise = 0.02

x = np.random.randn(n) * vals / 2
a, b, c = np.random.randn(3)
y = a*x*x + b*x  + c
noisey = y + noise * vals * np.random.randn(n)
print (f'coeffs are: {a}, {b}, {c}.')
print (y[:10])
#

matriX = np.stack( (np.square(x), x, np.ones(n)), axis=1)
print(f'shape of matriX \t\t: {matriX.shape}')
print(f'shape of matriX.transpose \t: {matriX.transpose().shape}')
u = inv(matriX.T@matriX)@matriX.T
print(f'shape of u: {u.shape}')
u = u@y
print(f'shape of u: {u.shape}')

print(u)

# plot data and fit function
xp = np.arange(-vals, vals, vals / 15)
yp = u[0]*xp*xp + u[1]*xp + u[2]

plt.plot(x, y, 'bo')
plt.plot(x, noisey, 'r+')
plt.plot(xp, yp, 'g-')
plt.show()


