from sympy import Symbol, Derivative
import numpy as np
import time
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LogNorm
from collections import deque

class Plot3D():
    def __init__(self, noOfPoints, function, margin):
        self.numberOfPoints = noOfPoints
        self.f = function
        margin = margin
        self.x_min, self.y_min = 0.0 - margin, 0.0 - margin
        self.x_max, self.y_max = 0.0 + margin, 0.0 + margin
        self.x_points = np.linspace(self.x_min, self.x_max, self.numberOfPoints)
        self.y_points = np.linspace(self.y_min, self.y_max, self.numberOfPoints)
        self.x_mesh, self.y_mesh = np.meshgrid(self.x_points, self.y_points)
        self.z = self.getMeshSolution()

    def getMeshSolution(self):
        count = 0
        funcValue = []
        for xi, yi in zip(self.x_mesh, self.y_mesh):
            for val in xi:
                funcValue.append(self.f.subs([(x, val),(y,yi[0])]))
        z = np.array(funcValue).reshape(self.numberOfPoints, self.numberOfPoints)
        return z
        #np.array([f.subs(xps, yps) for xps, yps in zip(x_mesh, y_mesh)])

    def plotMinima(self):
        
        fig = plt.figure(figsize=(10, 8))
        ax = plt.axes(projection='3d', elev=80, azim=-100)

        ax.plot_surface(self.x_mesh.astype(float), self.y_mesh.astype(float), self.z.astype(float), norm=LogNorm(), rstride=1, cstride=1, 
                edgecolor='none', alpha=.8, cmap=plt.cm.jet)
        
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')

        ax.set_xlim((self.x_min, self.x_max))
        ax.set_ylim((self.y_min, self.y_max))

        plt.show()

    def plotMinimaWithPath(self, path, opt):
        fig = plt.figure(figsize=(10,8))
        ax = plt.axes(projection='3d', elev=80, azim=-100)

        ax.plot_surface(self.x_mesh.astype(float), self.y_mesh.astype(float), self.z.astype(float), norm=LogNorm(), rstride=1, cstride=1, 
                edgecolor='none', alpha=.8, cmap=plt.cm.jet)
        funcStart = []
        funcEnd = []
        for i in range(0, len(path[0,:-1])):
            funcStart.append(opt.func([path[0, i], path[1, i]]))
        for i in range(0, len(path[0,:-1])):
            funcEnd.append(opt.func([path[0, i+1], path[1, i+1]])-opt.func([path[0, i], path[1, i]]))

        ax.quiver(path[0,:-1], path[1,:-1], funcStart,
          path[0,1:]-path[0,:-1], path[1,1:]-path[1,:-1],
          funcEnd,
          color='k', length=1, normalize=True)
        
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')

        ax.set_xlim((self.x_min, self.x_max))
        ax.set_ylim((self.y_min, self.y_max))

        plt.show()

    def contourPlotWithPath(self, path):
        fig, ax = plt.subplots(figsize=(10, 8))

        ax.contour(self.x_mesh, self.y_mesh, self.z, levels=np.logspace(-.5, 5, 35), norm=LogNorm(), cmap=plt.cm.jet)
        
        ax.quiver(path[0,:-1].astype(float), path[1,:-1].astype(float), path[0,1:].astype(float)-path[0,:-1].astype(float), path[1,1:].astype(float)-path[1,:-1].astype(float),
                scale_units='xy', angles='xy', scale=1, color='k')

        ax.set_xlabel('x')
        ax.set_ylabel('y')

        ax.set_xlim((self.x_min, self.x_max))
        ax.set_ylim((self.y_min, self.y_max))

        plt.show()

    def contourPlot(self):
        fig, ax = plt.subplots(figsize=(10, 8))

        ax.contour(self.x_mesh.astype(float), self.y_mesh.astype(float), self.z.astype(float), levels=np.logspace(-.5, 5, 35), norm=LogNorm(), cmap=plt.cm.jet)

        ax.set_xlabel('x')
        ax.set_ylabel('y')

        ax.set_xlim((self.x_min, self.x_max))
        ax.set_ylim((self.y_min, self.y_max))

        plt.show()


class Optimiser():
    def __init__(self, function, x_init=None, y_init=None, learning_rate=0.01, momentum=0.9, delay=1):
        self.function = function
        self.gradients = self.gradient(self.function)
        scale = 3.0
        self.vars = np.zeros([2])
        if x_init is not None:
            self.vars[0] = x_init
        else:
            self.vars[0] = np.random.uniform(low=-scale, high=scale)
        if y_init is not None:
            self.vars[1] = y_init
        else:
            self.vars[1] = np.random.uniform(low=-scale, high=scale)

        self.lr = learning_rate
        self.momentum = momentum
        self.velocity = np.zeros([2])

        self.q = deque()
        for _ in range(delay):
            self.q.append([self.velocity])

        self.z_history = []
        self.x_history = []
        self.y_history = []

    def gradient(self, function):
        gradx = Derivative(function, x).doit()
        grady = Derivative(function, y).doit()
        return [gradx, grady]

    def update_weights(self, grads, velocity):

        velocity = np.multiply(self.momentum, velocity) + np.multiply(self.lr, grads)
        self.vars = np.subtract(self.vars, velocity)[0]
        return velocity

    def history_update(self, z, x, y):
        self.z_history.append(z)
        self.x_history.append(x)
        self.y_history.append(y)

    def func(self, variables):
        xi, yi = variables
        z = self.function.subs([(x,xi),(y,yi)])
        return z

    def grads(self, variables):
        xi, yi = variables
        dx = self.gradients[0].subs([(x,xi), (y,yi)])
        dy = self.gradients[1].subs([(x,xi), (y,yi)])
        grad = [dx, dy]
        return grad

    def train(self, max_iter):
        zList = np.zeros(max_iter+1)
        for step in range(max_iter):
            
            currentVelocity = self.q.popleft()
            self.z = self.func(self.vars)
            zList[step+1] = self.z
            
            diff = np.abs(zList[step] - zList[step+1])
            
            self.history_update(self.z, self.x, self.y)

            self.grad = self.grads(self.vars)
            newVelo = self.update_weights(self.grad, currentVelocity)

            if (step+1) % 100 == 0:
                print("steps: {}  z: {:.6f}  x: {:.5f}  y: {:.5f}  dx: {:.5f}  dy: {:.5f}".format(step+1, self.func(self.vars), self.x, self.y, self.dx, self.dy))
            if np.abs(diff) < 1e-7 and step > 5:
                print("Enough convergence")
                print("steps: {}  z: {:.6f}  x: {:.5f}  y: {:.5f}".format(step+1, self.func(self.vars), self.x, self.y))
                self.z = self.func(self.vars)
                self.history_update(self.z, self.x, self.y)
                break
            self.q.append(newVelo)
                
            pre_z = self.z

        self.x_history = np.array(self.x_history)
        self.y_history = np.array(self.y_history)
        self.path = np.concatenate((np.expand_dims(self.x_history, 1), np.expand_dims(self.y_history, 1)), axis=1).T

    @property
    def x(self):
        return self.vars[0]

    @property
    def y(self):
        return self.vars[1]

    @property
    def dx(self):
        return self.grad[0]

    @property
    def dy(self):
        return self.grad[1]


x = Symbol('x')
y = Symbol('y')
f = (1.5 - x + x*y)**2 + (2.25 - x + x*y**2)**2 + (2.625 - x + x*y**3)**2
g = x**2 + y**2 + 4*x + 5*x

opt = Optimiser(f, 1.0, 1.0, momentum=0.8, delay=2)
opt.train(1000)

Plot3D = Plot3D(50, f, margin=4.5)
Plot3D.contourPlotWithPath(opt.path)