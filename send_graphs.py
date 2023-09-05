import requests


def send_telegram_files(token, chat_id, file_paths):
    url = f"https://api.telegram.org/bot{token}/sendDocument"

    for file_path in file_paths:
        files = {'document': open(file_path, 'rb')}
        data = {'chat_id': chat_id}

        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            print(f"Successfully sent {file_path}")
        else:
            print(f"Failed to send {file_path}. Status code: {response.status_code}, Response: {response.json()}")


if __name__ == "__main__":
    token = 'API_TOKEN'
    chat_id = 'CHAT_ID'
    file_paths = ['price_difference_graph.png', 'price_graph.png']

    send_telegram_files(token, chat_id, file_paths)