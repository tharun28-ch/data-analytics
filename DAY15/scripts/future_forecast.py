import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../data/daily_registrations.csv", parse_dates=['Date'], index_col='Date')

df['7Day_MA'] = df['Registrations'].rolling(window=7).mean()

last_ma_value = df['7Day_MA'].iloc[-1]
print(f"Forecasted Registrations for tomorrow: {last_ma_value:.2f}")

df['DayOfWeek'] = df.index.day_name()
avg_by_day = df.groupby('DayOfWeek')['Registrations'].mean().reindex([
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
])
print("Average Sign-ups by Day:")
print(avg_by_day)

peak_day = avg_by_day.idxmax()
print(f"Peak Day: {peak_day}")

plt.figure(figsize=(12, 6))
plt.plot(df['Registrations'], label='Actual Daily Sign-ups', alpha=0.3)
plt.plot(df['7Day_MA'], label='7-Day Trend Line', color='red', linewidth=2)
plt.title('MeetMux Growth Trend Analysis')
plt.xlabel('Date')
plt.ylabel('Registrations')
plt.legend()
plt.tight_layout()
plt.savefig('../docs/trend_analysis.png', dpi=150)
plt.show()
