import numpy as np
from scipy.stats import gamma
import matplotlib.pyplot as plt

# 假设的样本数据：呼叫中心每个呼叫之间的间隔时间（分钟）
call_intervals = np.array([5, 3, 6, 2, 4, 3, 7, 5, 4, 6, 2, 3, 5, 4, 3, 6, 2, 5, 7, 4, 3, 5, 2, 6, 4])

# 计算样本数据的平均值
mean_interval = np.mean(call_intervals)

# 选择分析等待前3个呼叫的总时间
k = 3  # 形状参数
theta = mean_interval / k  # 尺度参数

# 使用样本数据估计的参数来拟合伽马分布
alpha_est = k
beta_est = theta

mode = (alpha_est - 1) * beta_est if alpha_est > 1 else 0


# 生成伽马分布的PDF
x = np.linspace(0, call_intervals.max() * k, 100)
pdf = gamma.pdf(x, alpha_est, scale=beta_est)

# 绘制结果
plt.figure(figsize=(10, 6))
plt.plot(x, pdf, 'r-', lw=2, label=f'Gamma PDF (α={alpha_est}, β={beta_est:.2f})')
plt.hist(call_intervals * k, bins=30, density=True, alpha=0.6, color='g', label='Sample Histogram')
plt.title('Gamma Distribution of Call Intervals (Total time for 3 calls)')
plt.xlabel('Total Time (minutes)')
plt.ylabel('Density')
plt.legend()
plt.show()
