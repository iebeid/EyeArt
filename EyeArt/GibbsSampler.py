import random
import pandas
import numpy
import scipy.stats as stats
import pylab as plt
import pymc3

from progressbar import ProgressBar


def count_group(data,group):
    group_counter = 0
    for d in data:
        if d == group:
            group_counter = group_counter + 1
    return group_counter

def tabulate(data,groups):
    sums = []
    for group in groups:
        sum = count_group(data,group)
        sums.append(sum)
    return sums

def gibbs_sampler(niter,burnin,y,K,alpha,MuY_Mu0,MuY_SigmaSq0,SigmaSqY_a,SigmaSqY_b):
    n = y.size
    # gridFactor = 0.2 * stats.tstd(y)
    # ygrid = numpy.linspace(numpy.min(y)-gridFactor, numpy.max(y)+gridFactor, num=300)
    ygrid = numpy.linspace(numpy.min(y), numpy.max(y), num=300)
    density_est = numpy.zeros(((niter - burnin),ygrid.size))
    # PiY_MCMC = MuY_MCMC = numpy.zeros(((niter - burnin), K))
    # SigmaSqY_MCMC = numpy.zeros((niter - burnin))
    PiY = numpy.repeat(1 / K, K, axis=0)

    a = numpy.arange(1,K+1)

    Z = numpy.random.choice(a, size=n, replace=True, p=PiY)

    MuY = numpy.linspace(numpy.min(y), numpy.max(y), num=K)
    print("MuY: " + str(MuY))
    SigmaSqY = stats.tvar(y) / (2 * K)
    # SigmaSqY = stats.tvar(y)
    print("SigmaSqY: " + str(SigmaSqY))
    for mm in range(0,niter):
        #Update Z
        for ii in range(0,n):
            ZNormalDistributionPrior = stats.norm(loc=MuY, scale=numpy.sqrt(SigmaSqY)).pdf(y[ii])
            ProbsZ = PiY * ZNormalDistributionPrior
            # a = numpy.arange(1, K + 1)
            # I had to normalize because the probabilties passed to the sampling function, the sampling function in
            # python checks whether the summation of all probabiliites equals 1 without having any error tolerance
            probs = numpy.array(ProbsZ)
            probs /= probs.sum()
            probs.sum()
            # print(probs)
            Z[ii] = numpy.random.choice(a, size=1, replace=True, p=probs)

        # Update PiY
        groups = []
        for l in range(1,K+1):
            groups.append(l)
        ZFreqs = tabulate(Z, groups)
        PiY = []
        for m in range(0,K):
            randomVariate = stats.gamma.rvs((alpha / K + ZFreqs[m]))
            # randomVariate = stats.norm.rvs()
            # print(randomVariate)
            PiY.append(randomVariate)

        PiY = PiY / sum(PiY)



        # Update SigmaSqY
        sumOfMus = 0
        for o in range(0,n):
            MuValue = (y[o] - MuY[Z[o]-1]) * (y[o] - MuY[Z[o]-1])
            sumOfMus = sumOfMus + MuValue
        if (mm > burnin / 2):
            SigmaSqY = 1 / (stats.gamma.rvs((SigmaSqY_a+n / 2),scale=(1/(SigmaSqY_b+sumOfMus / 2))))

        # Update MuY
        for kk in range(1, K+1):
            temp = numpy.where(Z==kk)
            MuY_SigmaSq = 1 / (1 / MuY_SigmaSq0 + ZFreqs[kk-1] / SigmaSqY)
            MuY_Mu = MuY_SigmaSq * (MuY_Mu0 / MuY_SigmaSq0 + sum(y[temp]) / SigmaSqY)
            MuY[kk-1] = stats.norm.rvs(loc=MuY_Mu,scale=numpy.sqrt(MuY_SigmaSq))

        # Estimate density
        if (mm > burnin):
            # PiY_MCMC[(mm - burnin),] = PiY
            # MuY_MCMC[(mm - burnin),] = MuY
            # SigmaSqY_MCMC[mm - burnin] = SigmaSqY
            for kkk in range(1, K + 1):
                density_est[(mm - burnin),] = density_est[(mm-burnin), ]+PiY[kkk-1] * stats.norm(loc=MuY[kkk-1],scale=numpy.sqrt(SigmaSqY)).pdf(ygrid)



    print(ygrid.size)
    print(density_est.size)
    print(density_est[-1])
    print("Final Mean: " + str(stats.tmean(density_est[-1])))
    print("Final Variance: " + str(stats.tvar(density_est[-1])))

    plt.hist(y, normed=True, bins=30)
    plt.plot(ygrid, density_est[-1])
    plt.show()

if __name__ == "__main__":
    #Initialize random number generator
    random.seed(2018)

    #Algorithm parameters
    burnin = 100
    niter = 1000
    K = 3

    #Load galaxies dataset
    dataFile = "galaxies.csv"
    dataFrame = pandas.read_csv(dataFile, sep=',', na_values='.')
    dataFrame['velocties'] = dataFrame['velocties'].divide(1000)
    y = numpy.array(dataFrame['velocties'].tolist()).reshape(len(dataFrame['velocties'].tolist()),1)

    #Distribution parameters
    alpha = 1
    MuY_Mu0 = stats.tmean(y)
    print("Original Mean: " + str(stats.tmean(y)))
    print("Original Variance: " + str(stats.tvar(y)))
    MuY_SigmaSq0 = 5 * stats.tvar(y)
    SigmaSqY_a = 0.1
    SigmaSqY_b = 0.1

    #Create inverse gamma prior for sigma square and plot
    SigmaSqYgrid = numpy.linspace(0.0, stats.tvar(y), num=100)
    SigmaSqYprior = stats.invgamma(SigmaSqYgrid,loc=SigmaSqY_a,scale=SigmaSqY_b).pdf(SigmaSqYgrid)
    plt.plot(SigmaSqYgrid, SigmaSqYprior)
    plt.show()

    #Gibbs Sampler
    gibbs_sampler(niter,burnin,y,K,alpha,MuY_Mu0,MuY_SigmaSq0,SigmaSqY_a,SigmaSqY_b)