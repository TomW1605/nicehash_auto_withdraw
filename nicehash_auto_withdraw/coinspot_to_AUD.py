import configparser

import pushover_wrapper as pushover
from coinspot import CoinSpot

config = configparser.ConfigParser()
config.read('config.ini')

pushover_client = pushover.Client(config['pushover']['user_key'], api_token=config['pushover']['api_token'])

# initialise the library
client = CoinSpot(config['coinspot']['api_key'], config['coinspot']['api_secret'])

# get your coin wallet balances
balance = 0
try:
    balance = float(client.balances()['balance']['btc'])
except KeyError:
    print("No BTC funds")
    exit()

print(balance)

# Get a quote on buying a billion BTC, with estimation of timeframe
quote = client.quotesell('BTC', balance)['quote']
print(quote)

client.sell('BTC', balance, quote)

try:
    aud_balance = float(self.balances()['balance']['aud'])
except KeyError:
    print("No AUD funds")
    exit()
