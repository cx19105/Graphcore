from BaseOptimiser import Optimiser
import numpy as np

class OptimiserWithVaryingDelay(Optimiser):
    def __init__(self, function, varSymbols, varInits=None, tol=1e-7, learning_rate=0.01, momentum=0.9, variableMomentumScalar=None, meanDelay=1):
        super().__init__(function, varSymbols, varInits, tol, learning_rate, momentum, variableMomentumScalar, delay=None)
        self.meanDelay = meanDelay
        self.velocities = []
        self.velocities.append(self.velocity)

    def getProbability(self, meanDelay):
        mu = meanDelay
        sigma = 1
        dist = round(np.random.normal(mu, sigma))
        if dist <= 1:
            return 1
        else:
            return dist
        
    def getCurrentVelocity(self):
        delay = self.getProbability(self.meanDelay)
        if len(self.velocities) >= (delay + 1):
            return self.velocities[-delay]
        else:
            return self.velocities[0]

    def saveVelocity(self, newVelocity):
        self.velocities.append(newVelocity)

    def update_weights(self, grads, velocity):
        velocity = np.multiply(self.momentumVec, velocity) + np.multiply(self.lr, grads)
        self.varValues = np.subtract(self.varValues, velocity)
        return velocity

    def createPath(self):
        x_history = np.array(self.varValuesHistory[0])
        y_history = np.array(self.varValuesHistory[1])
        velocities = [np.array(self.diffValuesHistory[0])[:-1], np.array(self.diffValuesHistory[1])[:-1]]
        path = np.concatenate((np.expand_dims(x_history, 1), np.expand_dims(y_history, 1)), axis=1).T
        return velocities, path