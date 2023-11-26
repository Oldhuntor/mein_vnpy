import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# 生成模拟数据
np.random.seed(0)
true_slope = 2.0
true_intercept = 1.0
data_noise = 0.5
x_observed = np.linspace(0, 10, 20)
y_observed = true_slope * x_observed + true_intercept + np.random.normal(0, data_noise, len(x_observed))

# 定义模型参数的先验分布（正态分布）
prior_mean = np.array([0, 0])
prior_covariance = np.array([[1, 0], [0, 1]])

# 基于观测数据计算后验分布
X = np.vstack([np.ones_like(x_observed), x_observed]).T
likelihood_covariance = data_noise**2 * np.eye(len(x_observed))
posterior_covariance = np.linalg.inv(np.linalg.inv(prior_covariance) + np.dot(X.T, np.dot(np.linalg.inv(likelihood_covariance), X)))
posterior_mean = np.dot(posterior_covariance, np.dot(np.linalg.inv(prior_covariance), prior_mean) + np.dot(X.T, np.dot(np.linalg.inv(likelihood_covariance), y_observed)))

# 从后验分布中采样参数值
num_samples = 1000
parameter_samples = np.random.multivariate_normal(posterior_mean, posterior_covariance, num_samples)

# 生成新数据点的预测分布
x_new = np.linspace(0, 10, 100)
y_pred_samples = np.outer(parameter_samples[:, 1], x_new) + parameter_samples[:, 0][:, np.newaxis]

# 绘制预测分布
plt.figure(figsize=(10, 6))
plt.scatter(x_observed, y_observed, label='观测数据', color='blue', alpha=0.5)
for i in range(num_samples):
    plt.plot(x_new, y_pred_samples[i], color='red', alpha=0.1)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('线性回归模型的预测分布')
plt.legend()
plt.show()
