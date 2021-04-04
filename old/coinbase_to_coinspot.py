from coinbase.wallet.client import Client
from coinbase.wallet.error import ValidationError
import uuid

def round_down(value, decimals):
    factor = 1 / (10 ** decimals)
    return (value // factor) * factor

def send_all(api_key, api_secret, destination_address):
    client = Client(api_key, api_secret, api_version='2016-08-10')

    primary_account = client.get_primary_account()
    account_balance = float(primary_account["balance"]["amount"])
    print("Coinbase confirmed balance: "+str(account_balance)+" BTC")
    transfer_amount = round_down(account_balance, 4)

    if account_balance >= 0.0001:
        send = primary_account.send_money(to=destination_address, amount=account_balance, currency='BTC', idem=str(uuid.uuid4()), fee=0)
        '''while True:
            try:
                send = primary_account.send_money(to=destination_address, amount=transfer_amount, currency='BTC', idem=str(uuid.uuid4()), fee='0')
                print("Transferring "+str(transfer_amount)+" BTC, to crypto account: "+destination_address)
                break
            except ValidationError:
                print("Insufficient funds to cover Fees. Trying again")
                transfer_amount = transfer_amount-0.0001'''
        print(send)
