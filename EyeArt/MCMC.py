import random
import numpy as np
import pylab as pl
import scipy.special as ss
import pymc

pl.rcParams['figure.figsize'] = (17.0, 4.0)


# # Lets define our Beta Function to generate s for any particular state. We don't care for the normalizing constant here.
# def beta_s(w,a,b):
#     return w**(a-1)*(1-w)**(b-1)

# draw a random variable and check if it is greater than the acceptance criteria
def random_coin(p):
    unif = random.uniform(0, 1)
    if unif >= p:
        return False
    else:
        return True


# Actual Beta PDF.
def beta(a, b, i):
    e1 = ss.gamma(a + b)
    e2 = ss.gamma(a)
    e3 = ss.gamma(b)
    e4 = i ** (a - 1)
    e5 = (1 - i) ** (b - 1)
    return (e1 / (e2 * e3)) * e4 * e5


# Metropolis-Hastings algorithm for estimating a beta function
if __name__ == "__main__":
    a = 2
    b = 5
    number_of_states = 100000
    states = []
    cur = random.uniform(0, 1)
    for i in range(0, number_of_states):
        states.append(cur)
        next = random.uniform(0, 1)
        ap = min(beta(a, b, next) / beta(a, b, cur), 1)  # Calculate the acceptance probability
        if random_coin(ap):
            cur = next
    Ly = []
    Lx = []
    i_list = np.mgrid[0:1:100000j]
    for i in i_list:
        Lx.append(i)
        Ly.append(beta(a, b, i))
    pl.plot(Lx, Ly, label="Real Distribution: a=" + str(a) + ", b=" + str(b))
    # pl.ylim([0, 100])
    # pl.hist(states, bins=100, histtype='step', label="Simulated_MCMC: a=" + str(a) + ", b=" + str(b))
    pl.plot(Lx, states, label="Sampled Distribution: a=" + str(a) + ", b=" + str(b))
    # pl.ylim([0, 100])
    pl.legend()
    pl.show()
