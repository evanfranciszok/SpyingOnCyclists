import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('dataLog/completionTimeSmall.csv')

# Convert 'duration' column to numeric, coerce errors to NaN
df['duration'] = pd.to_numeric(df['duration'], errors='coerce')

# Convert 'duration' values to hours
df['duration'] = df['duration'] / 60

# Grouping data by 'name of dissemination case', 'number of bikes'
grouped_data = df.groupby(['name of dissemination case', 'number of bikes'])

# Calculate average roads per bike
df['roads_per_bike'] = df['number of bikes'] / df['roads']

# Create a new DataFrame to store the average duration for each case and number of bikes
average_duration_df = grouped_data[['duration', 'roads_per_bike']].mean().reset_index()

# Set up a dictionary to store individual axes for each case
axes_dict = {}

# Create a bar plot for each case
for name, group in average_duration_df.groupby('name of dissemination case'):
    # Combine SMALL and MEDIUM values and calculate the average
    combined_group = group.groupby('number of bikes')['duration'].mean().reset_index()

    # Create a new figure and axis for each case
    fig, ax = plt.subplots(figsize=(10, 6))
    axes_dict[name] = ax

    # Plotting bars for each map size
    ax.bar(combined_group['number of bikes'], combined_group['duration'], label=f'{name}')

    # Set labels and title
    ax.set_xlabel('Number of Bikes')
    ax.set_ylabel('Average Duration (minutes)')
    ax.set_title(f'Average Duration for {name}')
    ax.legend()

    # Annotate average duration (rounded to 2 decimal places) within each bar
    for container in ax.containers:
        for bar in container:
            height = bar.get_height()
            ax.annotate(f'{height:.0f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

# Adjust layout
plt.tight_layout()

# Show the plots
plt.show()
