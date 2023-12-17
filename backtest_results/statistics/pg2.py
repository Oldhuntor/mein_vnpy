"""
柏松伽马 交易策略研究

首先用长周期决定gamma分布先验

长周期是 7天的小时k 7 * 24 * 60 = 10080
然后计算24 小时中， 每天的上涨次数 ，{"day1": 13, "day2": 6, "day3": 8....}
计算出平均数和方差来估计 （MM） 先验的alpha prior 和 beta prior
短周期 
短周期的序列长度需要和长周期一样长吗？不一定
短周期数周期长度 k 不定
短周期的每周期最大上涨次数，24，也就是说，我需要 k 个 24 分钟构成的k线，总共 k * 24 分钟
得到短周期的数据 {"24k1": 13, "24k2": 12, "24k3":9 , .....}
最后更新后验分布 alpha post = alpha prior + 13 + 12 + 9 +...., beta post = beta prior + k


"""

from scipy.stats import poisson
# 重新导入必要的库
import numpy as np
from scipy.stats import gamma

# 泊松分布样本数据：呼叫中心每天接到的电话数量
poisson_samples = [15, 12, 17, 13, 18, 14, 16, 19, 15, 20]

# 伽马分布的先验参数
alpha_prior = 3
beta_prior = 1/5  # 因为伽马分布的尺度参数是1/lambda

# 使用泊松样本数据更新伽马分布的后验参数
alpha_posterior = alpha_prior + sum(poisson_samples)
beta_posterior = beta_prior + len(poisson_samples)

# 显示更新后的参数
print(alpha_posterior, beta_posterior)

# 从伽马分布的后验中生成随机样本
# 这些样本代表泊松分布的参数lambda的可能值
lambda_samples = np.random.gamma(alpha_posterior, 1/beta_posterior, 1000)

# 使用这些lambda样本来模拟未来一天的电话数量
predicted_calls = [poisson.rvs(l) for l in lambda_samples]

# 计算预测电话数量的一些统计数据
mean_calls = np.mean(predicted_calls)
median_calls = np.median(predicted_calls)
conf_int = np.percentile(predicted_calls, [2.5, 97.5])  # 95%置信区间

print(mean_calls, median_calls, conf_int)


# 计算在未来一天内接到超过20个电话的概率
prob_over_20 = np.mean([poisson.cdf(20, l) for l in lambda_samples])

# 计算在未来一周内每天平均接到至少15个电话的概率
# 我们可以先计算每天接到少于15个电话的概率，然后用1减去这个值
prob_at_least_15 = np.mean([1 - poisson.cdf(14, l) for l in lambda_samples])

print(prob_over_20, prob_at_least_15)

# 计算predictive distribution
data = 15
gamma.pdf(data, a=alpha_posterior, scale=1/beta_posterior)
lambda_space = np.linspace(0,30,1000)

prob_at_15 = np.sum([poisson.pmf(15, l)*gamma.pdf(l, a=alpha_posterior, scale=1/beta_posterior) for l in lambda_space])
from scipy.stats import poisson, gamma

prob_at_15 = np.sum(poisson.pmf(15, lambda_space) * gamma.pdf(lambda_space, a=alpha_posterior, scale=1/beta_posterior))
# Assuming lambda_space is an array of lambda values
delta_lambda = lambda_space[1] - lambda_space[0]  # Calculate the step size

# Compute the predictive probability, scaling by the step size
prob_at_15 = np.sum(poisson.pmf(15, lambda_space) * gamma.pdf(lambda_space, a=alpha_posterior, scale=1/beta_posterior)) * delta_lambda


post_prop = []
for x_new in np.arange(15,30,1):
    prob_new = np.sum(poisson.pmf(x_new, lambda_space) * gamma.pdf(lambda_space, a=alpha_posterior,
                                                                  scale=1 / beta_posterior)) * delta_lambda
    post_prop.append(prob_new)
post_prop = sum(post_prop)