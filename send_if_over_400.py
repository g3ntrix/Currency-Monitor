import sqlite3
import time
import requests


def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(f"Failed to send message: {response.content}")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")


def find_extreme_prices_and_notify(cursor, last_timestamp):
    latest_data, latest_timestamp = query_latest_data(cursor, last_timestamp)
    if not latest_data:
        return last_timestamp

    highest_sell = {'price': 0}
    lowest_buy = {'price': float('inf')}

    for _, exchange_name, buy_price, sell_price in latest_data:
        if sell_price > highest_sell['price']:
            highest_sell = {'exchange_name': exchange_name, 'price': sell_price}
        if buy_price < lowest_buy['price']:
            lowest_buy = {'exchange_name': exchange_name, 'price': buy_price}

    difference = highest_sell['price'] - lowest_buy['price']

    if difference >= 400:
        message = f"Max Sell Price: {highest_sell['price']} at {highest_sell['exchange_name']}\n" \
                  f"Min Buy Price: {lowest_buy['price']} at {lowest_buy['exchange_name']}\n" \
                  f"Price Difference: {difference}"

        bot_token = "API_TOKEN"
        group_chat_id = 'CHAT_ID'  # Replace with your actual chat ID
        send_telegram_message(bot_token, group_chat_id, message)

    print(f"Calculated price difference of {difference}")

    return latest_timestamp


def query_latest_data(cursor, last_timestamp):
    cursor.execute(
        "SELECT * FROM exchange_data WHERE timestamp > ? ORDER BY timestamp DESC",
        (last_timestamp,)
    )
    rows = cursor.fetchall()
    if rows:
        latest_timestamp = max(rows, key=lambda x: x[0])[0]
        return rows, latest_timestamp
    else:
        return [], last_timestamp


def main():
    conn = sqlite3.connect(
        'exchange_data.db')  # Make sure the database file is the same as the one your original script uses
    c = conn.cursor()

    last_timestamp = 0  # initialize to zero or any other value to represent the earliest time

    while True:
        last_timestamp = find_extreme_prices_and_notify(c, last_timestamp)
        time.sleep(10)  # Polling interval; can be adjusted, but we're checking the timestamp to not re-process records

    conn.close()


if __name__ == "__main__":
    main()
