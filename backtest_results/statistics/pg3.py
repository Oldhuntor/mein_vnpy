"""
柏松伽马 交易策略研究

一
首先用长周期决定gamma分布先验

长周期是 7天的小时k 7 * 24 * 60 = 10080
然后计算24 小时中， 每天的上涨次数 ，{"day1": 13, "day2": 6, "day3": 8....}
计算出平均数和方差来估计 （MM） 先验的alpha prior 和 beta prior
短周期
短周期的序列长度需要和长周期一样长吗？不一定
短周期数周期长度 k 不定
短周期的每周期最大上涨次数，24，也就是说，我需要 k 个 24 分钟构成的k线，总共 k * 24 分钟
得到短周期的数据 {"24k1": 13, "24k2": 12, "24k3":9 , .....}

二
最后更新后验分布 alpha post = alpha prior + 13 + 12 + 9 +...., beta post = beta prior + k


三
后验预测分布：

# 计算在未来24分钟内超过12时间区间是上涨的概率
prob_over_12 = np.mean([poisson.cdf(12, l) for l in lambda_samples])
"""


import numpy as np
from scipy.stats import gamma, poisson
import matplotlib.pyplot as plt
for i in range(5):
    # 模拟长周期（7天）的数据
    long_period_data = np.random.randint(0, 25, 50)  # 假设每天的最大上涨次数为24

    # 计算平均值和方差
    mean_long = np.mean(long_period_data)
    variance_long = np.var(long_period_data)

    # 估计伽玛分布的先验参数
    alpha_prior = mean_long**2 / variance_long
    beta_prior = mean_long / variance_long

    # 模拟短周期（24分钟）的数据
    short_period_data = np.random.randint(0, 25, size=5)  # 假设每24分钟周期的最大上涨次数为24

    # 更新后验分布参数
    alpha_posterior = alpha_prior + sum(short_period_data)
    beta_posterior = beta_prior + len(short_period_data)

    # 输出结果
    print(f"Alpha Prior: {alpha_prior}, Beta Prior: {beta_prior}")
    print(f"Alpha Posterior: {alpha_posterior}, Beta Posterior: {beta_posterior}")

    # 创建伽玛分布的先验和后验分布
    prior_dist = gamma(alpha_prior, scale = 1/beta_prior)
    posterior_dist = gamma(alpha_posterior, scale = 1/beta_posterior)
    lambda_samples = np.random.gamma(alpha_posterior, 1 / beta_posterior, 1000)

    # 生成伽玛分布的概率密度函数 (PDF) 数据
    x = np.linspace(0, 50, 100000)
    y_prior = prior_dist.pdf(x)
    y_posterior = posterior_dist.pdf(x)

    # 绘制图像
    plt.figure(figsize=(10, 6))
    plt.plot(x, y_prior, label='Prior Distribution')
    plt.plot(x, y_posterior, label='Posterior Distribution')
    plt.title('Gamma Distribution: Prior vs Posterior')
    plt.xlabel('Rate')
    plt.ylabel('Density')
    plt.legend()
    plt.show()

    prob_over_12 = np.mean([poisson.cdf(12, l) for l in lambda_samples])
    print(1-prob_over_12)