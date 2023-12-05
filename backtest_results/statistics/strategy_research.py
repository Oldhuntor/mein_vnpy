import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom, beta

# Parameters
short_size = 10  # Size of the short period
long_size = 5    # Size of the long period
theta_space = np.linspace(0, 1, 100)  # Possible values for theta (market up probability)

# Observed data
long_up = 2  # Number of ups in the long period
short_up = 10  # Number of ups in the short period

# Parameters for the Beta distribution (using long-term data)
alpha = long_up + 1
beta_param = long_size - long_up + 1

# Calculate priors based on long term data using Beta distribution
priors = beta.pdf(theta_space, alpha, beta_param)/100

# Likelihood for the short period data given different thetas
likelihoods = binom.pmf(short_up, short_size, theta_space)

# Calculate the evidence (normalizing constant)
evidence = np.sum(likelihoods * priors)

# Calculate the posterior distribution
posterior = (likelihoods * priors) / evidence
max_posterior_theta = theta_space[np.argmax(posterior)]
print(max_posterior_theta)

# Plotting the prior and posterior distributions
plt.figure(figsize=(12, 6))
plt.plot(theta_space, priors, label='Beta Prior', color='blue')
plt.plot(theta_space, posterior, label='Posterior', color='red')
plt.xlabel('Theta')
plt.ylabel('Density')
plt.title('Prior and Posterior Distributions')
plt.legend()
plt.grid(True)
plt.show()
