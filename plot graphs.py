import matplotlib.pyplot as plt
import pandas as pd

# Load data
pow_data = pd.read_csv('pow_blockchain_statistics.csv')
pow_plus_data = pd.read_csv('blockchain_statistics.csv')

# # Calculate total rewards for each checkpoint type and main blocks
# total_rewards_pow = {
#     'Checkpoint1': pow_data['Checkpoint1 Blocks Added'].sum(),
#     'Checkpoint2': pow_data['Checkpoint2 Blocks Added'].sum(),
#     'Checkpoint3': pow_data['Checkpoint3 Blocks Added'].sum(),
#     'Main': pow_data['Main Blocks Added'].sum()
# }

# Aggregate data for each checkpoint type
checkpoint1_pow_plus = pow_plus_data[['Miner', 'Checkpoint1 Blocks Added']].set_index('Miner')
checkpoint2_pow_plus = pow_plus_data[['Miner', 'Checkpoint2 Blocks Added']].set_index('Miner')
checkpoint3_pow_plus = pow_plus_data[['Miner', 'Checkpoint3 Blocks Added']].set_index('Miner')

# Plot function
def plot_checkpoint_blocks(checkpoint_data, checkpoint_name, title):
    miners = checkpoint_data.index
    blocks_added = checkpoint_data[checkpoint_name]
    
    plt.figure(figsize=(14, 7))
    plt.bar(miners, blocks_added, color='blue', align='center')
    plt.xlabel('Miner')
    plt.ylabel('Blocks Added')
    plt.title(title)
    plt.xticks(rotation=90)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Plotting for PoW++
plot_checkpoint_blocks(checkpoint1_pow_plus, 'Checkpoint1 Blocks Added', 'Checkpoint 1 Blocks Added by Miners (PoW++)')
plot_checkpoint_blocks(checkpoint2_pow_plus, 'Checkpoint2 Blocks Added', 'Checkpoint 2 Blocks Added by Miners (PoW++)')
plot_checkpoint_blocks(checkpoint3_pow_plus, 'Checkpoint3 Blocks Added', 'Checkpoint 3 Blocks Added by Miners (PoW++)')
# Calculate averages
avg_reward_pow = pow_data['Rewards'].mean()
avg_reward_pow_plus = pow_plus_data['Rewards'].mean()

# Plot
plt.figure(figsize=(10, 6))
plt.bar(['PoW', 'PoW++'], [avg_reward_pow, avg_reward_pow_plus], color=['skyblue', 'lightgreen'])
plt.xlabel('Protocol')
plt.ylabel('Average Reward')
plt.title('Average Reward per Miner')
# plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# Plot scatter plots
plt.figure(figsize=(14, 7))
plt.scatter(pow_data['Blocks Added'], pow_data['Rewards'], label='PoW', color='blue')
plt.scatter(pow_plus_data['Main Blocks Added'], pow_plus_data['Rewards'], label='PoW++', color='green')
plt.xlabel('Blocks Added')
plt.ylabel('Rewards')
plt.title('Reward vs. Number of Blocks Added')
plt.legend()
plt.grid(True)
plt.show()


# Calculate max rewards
max_reward_pow = pow_data['Rewards'].max()
max_reward_pow_plus = pow_plus_data['Rewards'].max()

# Plot
plt.figure(figsize=(10, 6))
plt.bar(['PoW', 'PoW++'], [max_reward_pow, max_reward_pow_plus], color=['skyblue', 'lightgreen'])
plt.xlabel('Protocol')
plt.ylabel('Maximum Reward')
plt.title('Maximum Reward per Miner')
plt.show()

# Calculate averages
avg_blocks_pow = pow_data['Blocks Added'].mean()
avg_blocks_pow_plus = pow_plus_data['Main Blocks Added'].mean()

# Plot
plt.figure(figsize=(10, 6))
plt.bar(['PoW', 'PoW++'], [avg_blocks_pow, avg_blocks_pow_plus], color=['blue', 'green'])
plt.xlabel('Protocol')
plt.ylabel('Average Blocks Added')
plt.title('Average Blocks Added per Miner')
plt.show()

# Count miners by blocks added
num_blocks_pow = pow_data['Blocks Added'].value_counts().sort_index()
num_blocks_pow_plus = pow_plus_data['Main Blocks Added'].value_counts().sort_index()

# Plot
plt.figure(figsize=(14, 7))
plt.plot(num_blocks_pow.index, num_blocks_pow.values, marker='o', label='PoW', color='blue')
plt.plot(num_blocks_pow_plus.index, num_blocks_pow_plus.values, marker='o', label='PoW++', color='green')
plt.xlabel('Number of Blocks Added')
plt.ylabel('Number of Miners')
plt.title('Number of Miners by Number of Blocks Added')
plt.legend()
plt.grid(True)
plt.show()


# Plot histogram
plt.figure(figsize=(14, 7))
plt.hist(pow_data['Rewards'], bins=20, alpha=0.5, label='PoW', color='blue')
plt.hist(pow_plus_data['Rewards'], bins=20, alpha=0.5, label='PoW++', color='green')
plt.xlabel('Rewards')
plt.ylabel('Number of Miners')
plt.title('Distribution of Rewards per Miner')
plt.legend()
plt.grid(True)
plt.show()

# Plot histogram
plt.figure(figsize=(14, 7))
plt.hist(pow_data['Blocks Added'], bins=20, alpha=0.5, label='PoW', color='blue')
plt.hist(pow_plus_data['Main Blocks Added'], bins=20, alpha=0.5, label='PoW++', color='green')
plt.xlabel('Blocks Added')
plt.ylabel('Number of Miners')
plt.title('Distribution of Blocks Added per Miner')
plt.legend()
plt.grid(True)
plt.show()
