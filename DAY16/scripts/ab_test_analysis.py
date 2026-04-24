import numpy as np
from scipy import stats

group_a = np.random.normal(50, 10, 30)
group_b = np.random.normal(58, 12, 30)

t_stat, p_value = stats.ttest_ind(group_a, group_b)

print(f"T-Statistic: {t_stat:.4f}")
print(f"P-Value: {p_value:.4f}")

alpha = 0.05
if p_value < alpha:
    print("Decision: Reject the Null Hypothesis. The change is Statistically Significant!")
else:
    print("Decision: Fail to Reject the Null. The difference is likely due to random chance.")
