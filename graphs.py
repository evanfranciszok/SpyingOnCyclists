import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('dataLog/completionTimeSmall.csv')

# Grouping data by 'name of dissemination case'
grouped_data = df.groupby('name of dissemination case')

# Creating subplots
fig, axs = plt.subplots(len(grouped_data), 1, figsize=(8, 4 * len(grouped_data)), sharey=True)

# Plotting scatter plots for each case
for i, (name, group) in enumerate(grouped_data):
    axs[i].scatter(group['duration'], group['number of bikes'], label=name)
    axs[i].set_title(f'Scatter Plot for {name}')
    axs[i].set_xlabel('Duration')
    axs[i].set_ylabel('Number of Bikes')
    axs[i].legend()

# Adjust layout
plt.tight_layout()

# Show the plot
plt.show()