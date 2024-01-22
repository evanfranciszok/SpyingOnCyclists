import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('dataLog/completionTimeSmall.csv')

# Convert 'duration' column to numeric, coerce errors to NaN
df['duration'] = pd.to_numeric(df['duration'], errors='coerce')

# Grouping data by 'name of dissemination case' and 'number of bikes'
grouped_data = df.groupby(['name of dissemination case', 'number of bikes'])

# Create a new DataFrame to store the average duration for each case and number of bikes
average_duration_df = grouped_data['duration'].mean().reset_index()

# # Create a new column 'undetermined' with value 43200 for the case 'undetermined'
# average_duration_df.loc[average_duration_df['name of dissemination case'] == 'undetermined', 'duration'] = 43200

# # Create a bar plot
# fig, ax = plt.subplots(figsize=(10, 6))

# # Plotting bars for each case
# for name, group in average_duration_df.groupby('name of dissemination case'):
#     ax.bar(group['number of bikes'], group['duration'], label=name)

# # Set y-axis range
# ax.set_ylim(0, 43200)

# # Add light grey bar for 'undetermined'
# undetermined_group = average_duration_df[average_duration_df['name of dissemination case'] == 'undetermined']
# ax.bar(undetermined_group['number of bikes'], undetermined_group['duration'],
#        color='lightgrey', label='undetermined')

# # Set labels and title
# ax.set_xlabel('Number of Bikes')
# ax.set_ylabel('Average Duration')
# ax.set_title('Average Duration for Different Cases and Number of Bikes')
# ax.legend()

# # Show the plot
# plt.show()

# Set up a dictionary to store individual axes for each case
axes_dict = {}

# Create a separate bar plot for each case
for name, group in average_duration_df.groupby('name of dissemination case'):
    # Create a new figure and axis for each case
    fig, ax = plt.subplots(figsize=(10, 6))
    axes_dict[name] = ax

    # Plotting bars for each case
    ax.bar(group['number of bikes'], group['duration'], label=name)

    # Set y-axis range
    ax.set_ylim(0, 43200)

    # Set labels and title
    ax.set_xlabel('Number of Bikes')
    ax.set_ylabel('Average Duration')
    ax.set_title(f'Average Duration for {name}')
    ax.legend()

# Adjust layout
plt.tight_layout()

# Show the plots
plt.show()