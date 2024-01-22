import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('dataLog/completionTimeSmall.csv')

# # Grouping data by 'name of dissemination case'
# grouped_data = df.groupby('name of dissemination case')

# # Creating subplots
# fig, axs = plt.subplots(len(grouped_data), 1, figsize=(8, 4 * len(grouped_data)), sharey=True)

# # Plotting scatter plots for each case
# for i, (name, group) in enumerate(grouped_data):
#     axs[i].scatter(group['duration'], group['number of bikes'], label=name)
#     axs[i].set_title(f'Scatter Plot for {name}')
#     axs[i].set_xlabel('Duration')
#     axs[i].set_ylabel('Number of Bikes')
#     axs[i].legend()

# # Adjust layout
# plt.tight_layout()

# # Show the plot
# plt.show()

# Calculate average number of bikes for each combination of dissemination case and number of bikes
average_data = data.groupby(['name of dissemination case', 'number of bikes']).mean().reset_index()

# Set the y-axis to range from 0 to the maximum duration in the CSV file
max_duration = data['duration'].max()

# Create a color map for different seeds
seed_colors = {10: 'red', 11: 'blue', 12: 'green', 13: 'orange', 14: 'purple'}

# Plot scatter plots for each dissemination case
for case, group in average_data.groupby('name of dissemination case'):
    plt.scatter(group['number of bikes'], group['duration'], c=group['seed'].map(seed_colors).fillna('gray'), label=f'{case}')

# Customize the plot
plt.title('Scatter Plots for Different Dissemination Cases')
plt.xlabel('Number of Bikes')
plt.ylabel('Duration')
plt.ylim(0, max_duration)  # Set y-axis limit
plt.legend(title='Dissemination Cases')

# Show the plot
plt.show()