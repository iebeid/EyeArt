import numpy as np
import math
import copy
from discreteMarkovChain import markovChain
import pandas
import numpy
import scipy
from scipy.sparse import csr_matrix

class Transition:
    def __init__(self, fromAOI=0, toAOI=0, count=0, numberOfTransitionsTillNow=0):
        self.fromAOI = fromAOI
        self.toAOI = toAOI
        self.count = count
        self.numberOfTransitionsTillNow = numberOfTransitionsTillNow

    def __eq__(self, other) :
        return self.__dict__ == other.__dict__

    def __str__(self):
        toBePrinted = "\n("+str(self.fromAOI)+" , "+str(self.toAOI)+")---->("\
                       +str(self.count)+"/"+str(self.numberOfTransitionsTillNow)+")"
        return toBePrinted

class TransitionMatrix:
    def __init__(self, numberOfStates, states):
        self.transitions = []
        self.states = copy.deepcopy(states)
        self.numberOfStates = numberOfStates
        self.T = np.zeros((self.numberOfStates, self.numberOfStates), dtype='float32')
        self.rawT = np.zeros((self.numberOfStates, self.numberOfStates), dtype='float32')
        self.S = np.zeros(self.numberOfStates, dtype='float32')
        self.estimatedS = np.zeros(self.numberOfStates, dtype='float32')
        self.transitionMatrixEntropy = 0
        self.stationaryDistributionEntropy = 0
        self.markovTest = 0
        if (self.numberOfStates != 0) and (self.states):
            # holds = self.test_markov_property()
            holds = True
            if holds:
                self.create_transtions()
                self.create_raw_transition_matrix()
                self.create_transition_matrix()
                self.estimate_pi_for_non_sparse_transition_matrix()
                self.compute_transition_matrix_normalized_entropy()
                self.compute_stationary_distribution_normalized_entropy()
            else:
                print("Sequence did not hold the Markov property")

    def test_markov_property(self):
        G_dense = self.rawT
        G_masked = numpy.ma.masked_values(G_dense, 0)
        G_sparse = csr_matrix(G_dense)

        print(G_sparse)

    def count_group(self, data, group):
        group_counter = 0
        for d in data:
            if d == group:
                group_counter = group_counter + 1
        return group_counter

    def tabulate(self, data, groups):
        sums = []
        for group in groups:
            sum = self.count_group(data, group)
            sums.append(sum)
        return sums

    def create_transtions(self):
        stateCounter = 0
        currentState = 0
        previousState = 0
        numberOfTransitions = int(len(self.states) - 1)
        for state in self.states:
            stateCounter = stateCounter + 1
            if stateCounter == 1:
                currentState = copy.deepcopy(state)
                previousState = copy.deepcopy(currentState)
            else:
                currentState = copy.deepcopy(state)
                transition = Transition(previousState, currentState, 0, numberOfTransitions)
                self.transitions.append(transition)
                previousState = copy.deepcopy(currentState)

    def create_transition_matrix(self):
        for transition in self.transitions:
            transitionHash = str(transition.fromAOI) + str(transition.toAOI)
            for lookupTransition in self.transitions:
                lookupTransitionHash = str(lookupTransition.fromAOI) + str(lookupTransition.toAOI)
                if transitionHash == lookupTransitionHash:
                    transition.count = transition.count + 1
            fromAOI = int(str(transition.fromAOI))
            toAOI = int(str(transition.toAOI))
            # probability = float(transition.count/transition.numberOfTransitionsTillNow)
            # self.T[toAOI, fromAOI] = probability
            self.T[toAOI-1, fromAOI-1] = transition.count
        for rows in range(self.numberOfStates):
            if self.T[rows].sum() > 0:
                self.T[rows] /= self.T[rows].sum()
            else:
                self.T[rows] = float(1/self.numberOfStates)

    def create_raw_transition_matrix(self):
        for transition in self.transitions:
            transitionHash = str(transition.fromAOI) + str(transition.toAOI)
            for lookupTransition in self.transitions:
                lookupTransitionHash = str(lookupTransition.fromAOI) + str(lookupTransition.toAOI)
                if transitionHash == lookupTransitionHash:
                    transition.count = transition.count + 1
            fromAOI = int(str(transition.fromAOI))
            toAOI = int(str(transition.toAOI))
            # probability = float(transition.count/transition.numberOfTransitionsTillNow)
            # self.T[toAOI, fromAOI] = probability
            self.rawT[toAOI-1, fromAOI-1] = transition.count
        for rows in range(self.numberOfStates):
            if self.rawT[rows].sum() > 0:
                self.rawT[rows] /= self.rawT[rows].sum()
            else:
                self.rawT[rows] = 0.0

    def estimate_pi_for_non_sparse_transition_matrix(self):
        mc = markovChain(self.T)
        mc.computePi('eigen')  # We can also use 'power', 'krylov' or 'eigen'
        self.estimatedS = np.nan_to_num(mc.pi)

    def compute_transition_matrix_normalized_entropy(self):
        en = 0.0
        for rows_i_from in range(0,self.numberOfStates):
            r = 0.0
            for col_j_to in range(0,self.numberOfStates):
                if self.T[rows_i_from, col_j_to] > 0:
                    r = r + (self.T[rows_i_from, col_j_to] * math.log2(self.T[rows_i_from, col_j_to]))
            value = self.estimatedS[rows_i_from] * r
            en = en + value
        en = -1.0 * en
        en = en / math.log2(self.numberOfStates)
        self.transitionMatrixEntropy = round(en,2)

    def compute_stationary_distribution_normalized_entropy(self):
        sen = 0.0
        value = 0.0
        for rows_i_from in range(0,self.numberOfStates):
            if self.estimatedS[rows_i_from] > 0:
                value = self.estimatedS[rows_i_from] * math.log2(self.estimatedS[rows_i_from])
            sen = sen + value
        sen = -1.0 * sen
        sen = sen / math.log2(self.numberOfStates)
        self.stationaryDistributionEntropy = round(sen,2)

    def __str__(self):
        m = ''
        for row in self.T: m = m + "\n" + str(' '.join('{0:.2f}'.format(x) for x in row))
        s = str(' '.join('{0:.2f}'.format(x) for x in self.estimatedS))
        toBePrinted = "Transition Matrix: \n" + str(m) \
                      + "\n\nStationary Distribution: \n\n" + str(s) \
                      + "\n\nTransition Matrix Entropy: " + str(self.transitionMatrixEntropy) \
                      + "\n\nStationary Distribution Entropy: " + str(self.stationaryDistributionEntropy) \
                      + "\n-------------\n"
        return toBePrinted