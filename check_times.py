import sqlite3


def count_occurrences_above_threshold(threshold):
    # Initialize SQLite database connection
    conn = sqlite3.connect('exchange_data.db')
    c = conn.cursor()

    try:
        # Query the database to find how many times the price difference was above the threshold
        c.execute("SELECT COUNT(*) FROM price_differences WHERE difference > ?", (threshold,))

        # Fetch the result
        count = c.fetchone()[0]

        print(f"greater than {threshold}: {count} times.")

        # Ask the user whether they want to save the date and time for each occurrence
        save_to_file = input("Do you want to print the date and time for each occurrence? (y/n): ")

        if save_to_file.lower() == 'y':
            # Query the database to get the date, time, and difference for each occurrence
            c.execute("SELECT timestamp, difference FROM price_differences WHERE difference > ?", (threshold,))
            results = c.fetchall()

            # Save the results in a file
            with open("occurrences.txt", "w") as f:
                for timestamp, difference in results:
                    f.write(f"{timestamp}: {difference}\n")

            print("date and time and diff.txt")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        # Close the database connection
        conn.close()


def main():
    # Ask the user for the threshold value
    threshold = int(input("threshold: "))

    # Run the function to count occurrences
    count_occurrences_above_threshold(threshold)


if __name__ == "__main__":
    main()
