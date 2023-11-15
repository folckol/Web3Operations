import requests
import json
import time
import hmac
import base64
from hashlib import sha256



api_key = ""
secret_key = ""
passphrase = ""


def get_signature(timestamp, method, request_path, body, secret_key):
    message = str(timestamp) + method + request_path + body
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod=sha256)
    d = mac.digest()
    return base64.b64encode(d)

def get_headers(api_key, signature, timestamp, passphrase):
    headers = {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': str(timestamp),
        'OK-ACCESS-PASSPHRASE': passphrase,
        'Content-Type': 'application/json'
    }
    return headers

def get_sub_account_eth_balances(timestamp):
    timestamp = get_server_time()
    method = 'GET'
    request_path = '/api/v5/account/subaccount/balances'
    body = ''
    signature = get_signature(timestamp, method, request_path, body, secret_key)
    headers = get_headers(api_key, signature, timestamp, passphrase)

    url = 'https://www.okx.com' + request_path
    response = requests.get(url, headers=headers)
    data = response.json()
    print(data)

    eth_balances = []

    if 'data' in data:
        for sub_account in data['data']:
            for balance in sub_account['balances']:
                if balance['ccy'] == 'ETH':
                    eth_balances.append({
                        'sub_account': sub_account['subAcct'],
                        'balance': float(balance['availBal'])
                    })

    return eth_balances

def transfer_eth_to_main_account(sub_account, amount, timestamp):
    timestamp = int(time.time())
    method = 'POST'
    request_path = '/api/v5/asset/transfer'
    body = json.dumps({
        'ccy': 'ETH',
        'amt': amount,
        'from': sub_account,
        'to': 'main',
        'instId': '',
        'toInstId': ''
    })
    signature = get_signature(timestamp, method, request_path, body, secret_key)
    headers = get_headers(api_key, signature, timestamp, passphrase)

    url = 'https://www.okx.com' + request_path
    response = requests.post(url, headers=headers, data=body)
    return response.json()

def withdraw_eth(amount, timestamp):
    timestamp = int(time.time())
    method = 'POST'
    request_path = '/api/v5/asset/withdrawal'
    body = json.dumps({
        'ccy': 'ETH',
        'toAddr': 'YOUR_ETH_ADDRESS',
        'amt': amount,
        'dest': '4'  # For OKX Chain
    })
    signature = get_signature(timestamp, method, request_path, body, secret_key)
    headers = get_headers(api_key, signature, timestamp, passphrase)

    url = 'https://www.okx.com' + request_path
    response = requests.post(url, headers=headers, data=body)
    return response.json()

def get_server_time():
    url = 'https://www.okx.com/api/v5/public/time'
    response = requests.get(url)
    data = response.json()
    if 'data' in data:
        # print(data)
        return data['data'][0]['ts']
    else:
        raise Exception("Failed to get server time")

def main():
    try:
        eth_balances = get_sub_account_eth_balances(get_server_time())
    except Exception as e:
        print(e)
        return

    total_eth_transferred = 0

    # Переводим ETH на основной аккаунт
    for balance_info in eth_balances:
        sub_account = balance_info['sub_account']
        balance = balance_info['balance']

        if balance > 0:
            try:
                transfer_result = transfer_eth_to_main_account(sub_account, balance, get_server_time())
                print(f"Transferred {balance} ETH from sub account {sub_account} to main account: {transfer_result}")
                total_eth_transferred += balance
            except Exception as e:
                print(f"Error transferring ETH from sub account {sub_account}: {e}")

    # Выводим ETH с биржи
    if total_eth_transferred > 0:
        try:
            withdrawal_result = withdraw_eth(total_eth_transferred, get_server_time())
            print(f"Withdrew {total_eth_transferred} ETH from main account: {withdrawal_result}")
        except Exception as e:
            print(f"Error withdrawing ETH: {e}")
    else:
        print("No ETH to transfer and withdraw")

if __name__ == "__main__":
    main()
