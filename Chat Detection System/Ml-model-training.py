import matplotlib.pyplot as plt

# Data for the crimes and their respective percentages
crimes = ['Cyberbullying', 'Online Harassment', 'Data Privacy Issues', 'Identity Theft', 'Financial Fraud']
percentages = [25, 20, 18, 15, 22]  # Example data for percentages of crimes

# Set the figure size and style
plt.figure(figsize=(10, 6))
bars = plt.bar(crimes, percentages, color=['#FF6347', '#3CB371', '#FFD700', '#1E90FF', '#8A2BE2'])

# Adding labels and title
plt.xlabel('Types of Cybercrimes', fontsize=12)
plt.ylabel('Percentage of Reported Cases', fontsize=12)
plt.title('Prevalence of Cybercrimes in India', fontsize=14)

# Add value labels on top of the bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 1, f'{yval}%', ha='center', va='bottom', fontsize=10)

# Adjust layout to fit the labels
plt.tight_layout()

# Show the plot
plt.show()
