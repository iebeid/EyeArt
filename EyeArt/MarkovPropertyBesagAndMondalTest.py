from TransitionMatrix import TransitionMatrix
import numpy

import numpy
import pandas
from TransitionMatrix import TransitionMatrix

import re

import rpy2.robjects as robjects


def normal_mu_mle(data):
    sum = 0
    T = data.size
    for datum in data:
        sum = sum + datum
    return float(sum/T)

def normal_sigma_squared_mle_biased(data,mu_hat):
    sum = 0
    T = data.size
    for datum in data:
        differenceSquared = (datum - mu_hat) * (datum - mu_hat)
        sum = sum + differenceSquared
    return float(sum/T)

def normal_sigma_squared_mle_unbiased(data,mu_hat):
    sum = 0
    T = data.size
    for datum in data:
        differenceSquared = (datum - mu_hat) * (datum - mu_hat)
        sum = sum + differenceSquared
    return float(sum/(T-1))

def augment_sequence(sequence):
    firstStateOfSequence = sequence[0]
    lastStateOfSequence = sequence[-1]
    sequence.append(lastStateOfSequence)
    sequence.append(firstStateOfSequence)

def check_markov_property(sequence):
    r = robjects.r
    r.source("C:/Users/islam/Desktop/testforgeneral.r")
    # r["main(sequence)"]
    x= robjects.IntVector(sequence)
    r_test_sequence = robjects.globalenv['main']
    p_value_string=r_test_sequence(x)
    p_value_extracted = re.findall("\d+\.\d+\d+", str(p_value_string))
    p_value = float(p_value_extracted[0])
    return p_value

if __name__ == "__main__":
    sequence = [1, 1, 4, 3, 2, 1, 4, 4, 2, 2, 3, 3, 2, 2, 1, 3, 2, 2, 1, 4, 4, 3, 3, 2, 1, 2, 2, 2, 2, 2, 2]
    r = check_markov_property(sequence)
    print(r)
    # sequence = [1, 1, 4, 3, 2, 1, 4, 4, 2, 2,
    #             3, 3, 2, 2, 1, 3, 2, 2, 1, 4, 4,
    #             3, 3, 2, 1, 2, 2, 2, 2, 2, 2]
    # augment_sequence(sequence)
    # states = numpy.unique(numpy.array(sequence))
    # transitionMatrix = TransitionMatrix(states.size, sequence)
    # print(transitionMatrix.states)
    # print(transitionMatrix.rawT)
    # print(transitionMatrix.estimatedS)
    # mu_mle = normal_mu_mle(transitionMatrix.rawT.flatten())
    # sigma_mle = normal_sigma_squared_mle_unbiased(transitionMatrix.rawT.flatten(),mu_mle)
    # print(mu_mle)
    # print(sigma_mle)
    # transitionMatrix.test_markov_property()