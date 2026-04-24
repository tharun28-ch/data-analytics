# Day 16: Hypothesis Testing & A/B Tests Reflection

## Section 1: The Null Hypothesis ($H_0$)
*   **Null Hypothesis ($H_0$)**: The change (e.g., a new blue button) had no effect on sign-ups.
*   **Alternative Hypothesis ($H_1$)**: The change did significantly increase sign-ups.

## Section 4: The Power Test (Sample Size Impact)
When running the T-Test with small vs large sample sizes:
*   **n = 5 days**: A small sample size leads to higher P-Values. The statistical test lacks the "power" to detect a real difference, often resulting in failing to reject the null hypothesis because the difference could easily be random noise.
*   **n = 500 days**: A large sample size provides high power. With so much data, the P-Value drops drastically, and even slight differences in the sample means become statistically significant. 

### Experiment Reflection
**Scenario:** On MeetMux, we changed the 'Join Now' button from Green to Orange. If our P-value is 0.24, should we tell the CEO that Orange is better? Why or why not?

**Answer:** No, we should not tell the CEO that the Orange button is better. A P-value of 0.24 indicates there is a 24% probability that the observed increase in sign-ups happened by pure random chance. Because 0.24 is greater than our significance level ($\alpha = 0.05$), we **Fail to Reject the Null Hypothesis**. The result is too noisy, and we lack the statistical evidence to confidently claim the change was successful.

### The "Golden Threshold"
**Why is a P-value of 0.05 the industry's golden threshold?**
Using 0.05 (or a 5% Significance Level) strikes a practical balance in business experiments. It ensures a 95% confidence that the observed results are not simply due to luck, acting as a stringent barrier against false positives (Type I errors). This prevents companies from wasting resources on rolling out "improvements" that are actually just random statistical fluctuations.
