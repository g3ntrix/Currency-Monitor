import requests
import sqlite3
import time
import json


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


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3'
    }

    try:
        response = requests.get(
            'AJAX_URL_TO_SCRAP',
            headers=headers)
        response.raise_for_status()
        return json.loads(response.text)
    except requests.RequestException as e:
        print(f"Network error: {e}")
        return None
    except json.JSONDecodeError:
        print("Failed to parse JSON")
        return None


def store_data(data, cursor, conn):
    try:
        for exchange in data['Exchanges']:
            buy_price = int(float(exchange['best_asks_price']))
            sell_price = int(float(exchange['best_bids_price']))
            exchange_name = exchange['title']
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO exchange_data VALUES (?, ?, ?, ?)",
                           (timestamp, exchange_name, buy_price, sell_price))
            print(f"Stored data for {exchange_name}: Buy = {buy_price}, Sell = {sell_price}")

        find_and_store_extreme_prices(cursor, conn)
    except sqlite3.Error as e:
        print(f"Database error: {e}")


def find_and_store_extreme_prices(cursor, conn):
    latest_data = query_latest_data(cursor)
    highest_sell = {'price': 0}
    lowest_buy = {'price': float('inf')}

    for _, exchange_name, buy_price, sell_price in latest_data:
        if sell_price > highest_sell['price']:
            highest_sell = {'exchange_name': exchange_name, 'price': sell_price}
        if buy_price < lowest_buy['price']:
            lowest_buy = {'exchange_name': exchange_name, 'price': buy_price}

    difference = highest_sell['price'] - lowest_buy['price']
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("INSERT INTO price_differences VALUES (?, ?, ?, ?)",
                   (timestamp, highest_sell['price'], lowest_buy['price'], difference))
    conn.commit()

    message = f"Max Sell Price: {highest_sell['price']} at {highest_sell['exchange_name']}\n" \
              f"Min Buy Price: {lowest_buy['price']} at {lowest_buy['exchange_name']}\n" \
              f"Price Difference: {difference}"

    bot_token = "BOT_TOKEN"
    group_chat_id = 'CHAT_ID'  # Replace with your actual chat ID (usually a negative number)
    send_telegram_message(bot_token, group_chat_id, message)

    print(f"Stored price difference of {difference} for {timestamp}")


def query_latest_data(cursor):
    cursor.execute("SELECT * FROM exchange_data WHERE timestamp = (SELECT MAX(timestamp) FROM exchange_data)")
    return cursor.fetchall()


def main():
    conn = sqlite3.connect('exchange_data.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS exchange_data
                (timestamp TEXT, exchange_name TEXT, buy_price INTEGER, sell_price INTEGER)''')

    c.execute('''CREATE TABLE IF NOT EXISTS price_differences
                (timestamp TEXT, highest_sell_price INTEGER, lowest_buy_price INTEGER, difference INTEGER)''')

    conn.commit()

    while True:
        data = fetch_data()
        if data:
            store_data(data, c, conn)
        time.sleep(10)

    conn.close()


if __name__ == "__main__":
    main()
