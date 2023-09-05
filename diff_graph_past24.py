import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def query_price_differences(cursor, start_time):
    cursor.execute("SELECT * FROM price_differences WHERE timestamp >= ?", (start_time,))
    return cursor.fetchall()


def main():
    # Initialize SQLite database connection
    conn = sqlite3.connect('exchange_data.db')
    c = conn.cursor()

    # Generate a timestamp for 24 hours ago
    # Assuming the timestamp in the database is in the format 'YYYY-MM-DD HH:MM:SS'
    time_now = datetime.now()
    time_24_hours_ago = time_now - timedelta(days=1)
    time_24_hours_ago_str = time_24_hours_ago.strftime('%Y-%m-%d %H:%M:%S')

    # Query price differences from the database for the past 24 hours
    all_data = query_price_differences(c, time_24_hours_ago_str)

    if len(all_data) == 0:
        print("No data found in the database for the past 24 hours.")
        return

    # Strip seconds from timestamps and prepare data for plotting
    timestamps = [record[0][:-3] for record in all_data]  # Remove seconds
    differences = [record[-1] for record in all_data]

    plot_times = [timestamps[0]]
    plot_values = [differences[0]]

    for i in range(1, len(timestamps)):
        if differences[i] != plot_values[-1]:
            plot_times.extend([timestamps[i - 1], timestamps[i]])
            plot_values.extend([differences[i - 1], differences[i]])

    # Adjust the figure size
    plt.figure(figsize=(10, 6))

    plt.plot(plot_times, plot_values, marker='o')
    plt.xlabel('Timestamp')
    plt.ylabel('Price Difference')
    plt.title('Price Difference Over Time (Last 24 hours)')

    # Reduce the number of x-ticks for better readability
    step = len(plot_times) // 10
    if step == 0:
        step = 1
    plt.xticks(plot_times[::step], rotation=45)

    # Add grid lines with 50% opacity
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5)

    # Adjust layout to ensure labels fit inside the figure
    plt.tight_layout()

    # Generate a unique file name based on the start and end timestamps
    start_time_str = time_24_hours_ago.strftime('%Y%m%d%H%M%S')  # Format: YYYYMMDDHHMMSS
    end_time_str = time_now.strftime('%Y%m%d%H%M%S')  # Format: YYYYMMDDHHMMSS
    unique_filename = f"price_difference_graph_{start_time_str}_to_{end_time_str}.png"

    # Save the figure with the unique filename
    plt.savefig(unique_filename)

    print(f"Graph saved as {unique_filename}")


if __name__ == "__main__":
    main()
