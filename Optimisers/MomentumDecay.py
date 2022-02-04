from BaseOptimiser import Optimiser
import numpy as np
from sympy import exp

class OptimiserWithMomentumDecay(Optimiser):
    def __init__(self, function, varSymbols, varInits=None, **kwargs):
        super().__init__(function, varSymbols, varInits, **kwargs)
        self.variableMomentumScalar = kwargs['variable_momentum_scalar']
        self.momentumDecay = True
        self.oscillations = []
        self.iterateRange = 10
        self.momentumPoint = 0.75
        for dim in range(len(varSymbols)):
            self.oscillations.append([])

    def variableMomentum(self, step):
        for index, dnHistory in enumerate(self.diffValuesHistory):
            isOscillating = self.checkOscillating(step, dnHistory)
            self.oscillations[index].append(isOscillating)
            if isOscillating:
                oscillationFreq = self.getOscillatingFrequency(index)
                #Only change the momentum if the oscillation frequency is over a threshold
                    #Updating the momentum
                self.momentumVec[index] = self.updateMomentum(self.momentumVec[index], oscillationFreq)

    def updateMomentum(self, currentMomentum, oscillationFreq):
        pointOfInflection = self.iterateRange*self.momentumPoint
        sigmoidFactor = (1-self.variableMomentumScalar/(1+exp(-(oscillationFreq-pointOfInflection))))
        return sigmoidFactor*currentMomentum

    def checkOscillating(self, step, dnHistory):
        dn1 = dnHistory[step]
        dn2 = dnHistory[step - 1]
        #Checking if the gradient has changed direction
        if dn1 * dn2 < 0:
            return True
        else:
            return False

    def getOscillatingFrequency(self, dim):
        
        #Returns the number of oscillations in the last ten iterates
        return sum(self.oscillations[dim][-self.iterateRange:])
    

            

   
