import numpy as np
import pymc3 as pm

if __name__ == "__main__":
    species = ['lions', 'tigers', 'bears']
    # Observations from multiple trips
    c = np.array([[3, 2, 1],
                  [2, 3, 1],
                  [3, 2, 1],
                  [2, 3, 1]])
    #Pseudocounts
    alphas = np.array([1, 1, 1])
    expected = (alphas + c) / (c.sum() + alphas.sum())

    # Create model
    with pm.Model() as model:
        # Parameters are a dirichlet distribution
        parameters = pm.Dirichlet('parameters', a=alphas, shape=3)
        # Observed data is a multinomial distribution
        observed_data = pm.Multinomial(
            'observed_data', n=6, p=parameters, shape=3, observed=c)

        trace = pm.sample(draws=1000, chains=2, tune=500, discard_tuned_samples=True)

        samples = pm.sample_ppc(trace, samples=1000)