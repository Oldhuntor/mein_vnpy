import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # Or another interactive backend like 'Qt5Agg'

# Assuming your text file is named 'data.txt' and uses comma as the separator
file_path = '/Users/huangxuanhao/Desktop/MyProject/mein_vnpy/output.txt'
df = pd.read_csv(file_path, sep=',', names=['time','postUp', 'postDown'])

# Now df is a DataFrame containing the data from your text file
print(df)


# Convert 'time' column to datetime
df['time'] = pd.to_datetime(df['time'])
# Define the date range
start_date = pd.Timestamp('2023-10-07 11:00:00+02:00')
end_date = pd.Timestamp('2023-10-7 23:59:59+02:00')

# Filter the DataFrame
df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]
timestamps_to_mark = [
    pd.Timestamp("2023-10-07 14:35:00+02:00"),
    pd.Timestamp("2023-10-07 16:00:00+02:00"),
    pd.Timestamp("2023-10-07 20:05:00+02:00"),
    pd.Timestamp("2023-10-07 15:30:00+02:00")
]
# Plotting
plt.figure(figsize=(10, 6))
plt.plot(df['time'], df['postUp'], label='postUp', color='blue')
plt.plot(df['time'], df['postDown'], label='postDown', color='red')
for dt in timestamps_to_mark:
    plt.scatter(dt, df.loc[df['time'] == dt, 'postUp'], color='green')  # Change 'postUp' to the column you want to mark
    plt.scatter(dt, df.loc[df['time'] == dt, 'postDown'], color='orange')  # Change 'postDown' if needed

plt.xlabel('Time')
plt.xlabel('Time')
plt.ylabel('Value')
plt.title('postUp and postDown over Time')
plt.legend()
plt.show()