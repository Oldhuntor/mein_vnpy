import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom, beta

# Parameters
short_size = 10  # Size of the short period
long_size = 30    # Size of the long period
theta_space = np.linspace(0, 1, 1000)  # Possible values for theta

# Observed data
long_up = 20  # Number of ups in the long period
short_up = 4  # Number of ups in the short period

# Beta distribution parameters
alpha = long_up
beta_param = long_size - long_up

# Calculate priors using Beta distribution
priors = beta.pdf(theta_space, alpha, beta_param)

# Normalize the priors
priors /= np.trapz(priors, theta_space)

# Likelihood for the short period data given different thetas
likelihoods = binom.pmf(short_up, short_size, theta_space)

# Calculate the posterior distribution
cal_posterior = likelihoods * priors
cal_posterior /= np.trapz(cal_posterior, theta_space)  # Normalize the posterior

# Finding the theta value corresponding to the maximum posterior probability
# posterior /= sum(posterior) # Normalize the posterior
posterior = beta.pdf(theta_space, alpha + short_up, beta_param + short_size - short_up)
posterior /= np.trapz(posterior, theta_space)  # Normalize the posterior

# predictive posterior
pred_post = (alpha + short_up) / (alpha + beta_param + short_size)

max_posterior_value = posterior.max()
print(f"max_posterior_value:{max_posterior_value}")
max_posterior_theta = theta_space[np.argmax(posterior)]

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(theta_space, cal_posterior, label='cal Beta Posterior', color='blue')
plt.plot(theta_space, posterior, label='Normalized Posterior', color='red')
plt.xlabel('Theta')
plt.ylabel('Density')
plt.title('Prior and Posterior Distributions')
plt.legend()
plt.grid(True)
plt.show()

max_posterior_theta, max_posterior_value

