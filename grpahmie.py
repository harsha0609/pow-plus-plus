import pandas as pd
import matplotlib.pyplot as plt

# Load data into pandas DataFrames
pow_data = pd.read_csv('pow_blockchain_statistics.csv')
pow_plus_data = pd.read_csv('blockchain_statistics.csv')

# Merge the dataframes on 'Miner'
df = pd.merge(pow_data[['Miner', 'Rewards']],
              pow_plus_data[['Miner', 'Rewards']],
              on='Miner',
              suffixes=('_pow', '_pow_plus_plus'))

# Plotting
plt.figure(figsize=(14, 7))
plt.plot(df['Miner'], df['Rewards_pow_plus_plus'], marker='o', linestyle='-', color='skyblue', label='POW++ Rewards')
plt.plot(df['Miner'], df['Rewards_pow'], marker='o', linestyle='-', color='lightgreen', label='POW Rewards')

plt.xlabel('Miners')
plt.ylabel('Total Rewards')
plt.title('Rewards at 100th block Comparison: POW++ vs POW')

# Remove x-axis labels
plt.xticks([])  # Hides the x-axis labels

plt.legend()
plt.grid(True)
plt.tight_layout()

# Save the plot as a file
plt.savefig('rewards_comparison.png')

# Show the plot
plt.show()

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data into pandas DataFrames
pow_data = pd.read_csv('pow_blockchain_statistics.csv')
pow_plus_data = pd.read_csv('blockchain_statistics.csv')

# Merge the dataframes on 'Miner'
df = pd.merge(pow_data[['Miner', 'Blocks Added']],
              pow_plus_data[['Miner', 'Blocks Added']],
              on='Miner',
              suffixes=('_pow', '_pow_plus_plus'))

# Set positions and width for the bars
bar_width = 0.35
index = np.arange(len(df['Miner']))

# Plotting
plt.figure(figsize=(16, 8))

# Plot bars for Blocks Added
plt.bar(index - bar_width / 2, df['Blocks Added_pow'], bar_width, label='Blocks Added POW', color='lightgreen')
plt.bar(index + bar_width / 2, df['Blocks Added_pow_plus_plus'], bar_width, label='Blocks Added POW++', color='skyblue')

plt.xlabel('Miners')
plt.ylabel('Number of Blocks Added')
plt.title('Blocks Added Comparison: POW vs POW++')

# Add x-axis labels
plt.xticks(index, df['Miner'], rotation=90)  # Rotate x-axis labels for better readability

# Add a legend
plt.legend()

# Add grid for better readability
plt.grid(True, linestyle='--', alpha=0.7)

# Adjust layout
plt.tight_layout()

# Save the plot as a file
plt.savefig('blocks_added_comparison.png')

# Show the plot
plt.show()

import pandas as pd
import matplotlib.pyplot as plt

# Load data into pandas DataFrames
pow_data = pd.read_csv('pow_blockchain_statistics.csv')
pow_plus_data = pd.read_csv('blockchain_statistics.csv')

# Filter the POW++ data
df_pow_plus = pow_data[['Miner', 'Blocks Added', 'Rewards']]

# Sort by Miner for consistency in x-axis
# df_pow_plus_sorted = df_pow_plus.sort_values('Miner')

# Plotting
plt.figure(figsize=(14, 7))

# Bar chart for blocks added
plt.plot(df_pow_plus['Miner'], df_pow_plus['Blocks Added'], marker='o', linestyle='-', color='skyblue', label='Blocks Added')

# Line chart for rewards
plt.plot(df_pow_plus['Miner'], df_pow_plus['Rewards'], marker='o', linestyle='-', color='lightgreen', label='Rewards')

plt.xlabel('Miner')
plt.ylabel('Blocks Added / Rewards')
plt.title('POW++: Blocks Added and Rewards by Miner')

# Rotate x-axis labels for better readability
plt.xticks([])

# Add a legend
plt.legend()

# Add grid for better readability
plt.grid(True, linestyle='--', alpha=0.7)

# Adjust layout
plt.tight_layout()

# Save the plot as a file
plt.savefig('pow_blocks_rewards.png')

# Show the plot
plt.show()
