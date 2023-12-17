import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gamma

# Define parameters for different gamma distributions with beta as the rate parameter
parameters = [(1, 1), (2, 1), (3, 1), (2, 2)]
x = np.linspace(0, 10, 1000)

# Plotting
plt.figure(figsize=(12, 8))
for alpha, beta in parameters:
    dist = gamma(a=alpha, scale=1/beta)  # Using scale as the inverse of rate
    plt.plot(x, dist.pdf(x), label=f'alpha={alpha}, beta={beta}')

plt.title('Gamma Distribution with Beta as Rate Parameter')
plt.xlabel('x')
plt.ylabel('Probability Density')
plt.legend()
plt.grid(True)
plt.show()
