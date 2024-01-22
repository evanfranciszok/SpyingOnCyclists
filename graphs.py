import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('dataLog/completionTimeSmall.csv')

# Convert 'duration' column to numeric, coerce errors to NaN
df['duration'] = pd.to_numeric(df['duration'], errors='coerce')

# Grouping data by 'name of dissemination case' and 'number of bikes'
grouped_data = df.groupby(['name of dissemination case', 'number of bikes'])

# Create a new DataFrame to store the average duration for each case and number of bikes
average_duration_df = grouped_data['duration'].mean().reset_index()

# Set up a dictionary to store individual axes for each case
axes_dict = {}

# Create a separate bar plot for each case
for name, group in average_duration_df.groupby('name of dissemination case'):
    # Create a new figure and axis for each case
    fig, ax = plt.subplots(figsize=(10, 6))
    axes_dict[name] = ax

    # Plotting bars for each case
    bars = ax.bar(group['number of bikes'], group['duration'], label=name)

    # Set y-axis range
    ax.set_ylim(0, 45000) # Adjusted range for better visualization

    # Set labels and title
    ax.set_xlabel('Number of Bikes')
    ax.set_ylabel('Average Duration')
    ax.set_title(f'Average Duration for {name}')
    ax.legend()

    # Annotate average duration above each bar
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', rotation='vertical')

# Adjust layout
plt.tight_layout()

# Show the plots
plt.show()