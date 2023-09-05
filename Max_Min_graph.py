import sqlite3
import matplotlib.pyplot as plt
import numpy as np

def create_graph():
    # Connect to SQLite database
    conn = sqlite3.connect('exchange_data.db')
    cursor = conn.cursor()

    # Initialize lists to store data
    timestamps = []
    max_sell_prices = []
    min_buy_prices = []

    # Fetch unique timestamps from the database
    cursor.execute("SELECT DISTINCT timestamp FROM exchange_data ORDER BY timestamp")
    unique_timestamps = cursor.fetchall()

    for timestamp_tuple in unique_timestamps:
        timestamp = timestamp_tuple[0]
        timestamp = timestamp[:-3]  # Removing seconds from timestamp
        timestamps.append(timestamp)

        # Fetch highest sell price for this timestamp
        cursor.execute("SELECT MAX(sell_price) FROM exchange_data WHERE timestamp=?", (timestamp_tuple[0],))
        max_sell = cursor.fetchone()[0]
        max_sell_prices.append(max_sell)

        # Fetch lowest buy price for this timestamp
        cursor.execute("SELECT MIN(buy_price) FROM exchange_data WHERE timestamp=?", (timestamp_tuple[0],))
        min_buy = cursor.fetchone()[0]
        min_buy_prices.append(min_buy)

    # Create graph
    fig, ax = plt.subplots(figsize=(15, 6))

    def plot_dotted_line(ax, x, y, label):
        unique_y = []
        unique_x = []
        for i in range(len(y)):
            if i == 0 or i == len(y) - 1 or y[i] != y[i - 1]:
                unique_y.append(y[i])
                unique_x.append(x[i])
        ax.plot(x, y, label=label)
        ax.scatter(unique_x, unique_y, marker='o')

    plot_dotted_line(ax, timestamps, max_sell_prices, 'Max Sell Price')
    plot_dotted_line(ax, timestamps, min_buy_prices, 'Min Buy Price')

    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Price')
    ax.set_title('Highest Sell and Lowest Buy Prices Over Time')

    # Configure x-axis labels
    plt.xticks(rotation=45)
    ax = plt.gca()

    # Show only every nth tick to prevent overcrowding
    n = len(timestamps) // 10  # Show only 10 labels on the x-axis
    if n == 0: n = 1  # Prevent division by zero

    for index, label in enumerate(ax.xaxis.get_ticklabels()):
        if index % n != 0:
            label.set_visible(False)

    ax.legend()
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5)  # Updated line to set grid opacity
    plt.tight_layout()  # Automatically adjust subplot params for better layout

    # Save the graph as a PNG file
    plt.savefig('price_graph.png')

    # Close the database connection
    conn.close()

if __name__ == '__main__':
    create_graph()
