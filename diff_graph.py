import sqlite3
import matplotlib.pyplot as plt


def query_price_differences(cursor):
    cursor.execute("SELECT * FROM price_differences")
    return cursor.fetchall()


def main():
    # Initialize SQLite database connection
    conn = sqlite3.connect('exchange_data.db')
    c = conn.cursor()

    # Query all price differences from the database
    all_data = query_price_differences(c)

    if len(all_data) == 0:
        print("No data found in the database.")
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
    plt.title('Price Difference Over Time')

    # Reduce the number of x-ticks for better readability
    step = len(plot_times) // 10
    if step == 0:
        step = 1
    plt.xticks(plot_times[::step], rotation=45)

    # Add grid lines with 50% opacity
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.5)  # Updated line to set grid opacity

    # Adjust layout to ensure labels fit inside the figure
    plt.tight_layout()

    # Save the figure as a PNG file
    plt.savefig("price_difference_graph.png")


if __name__ == "__main__":
    main()
