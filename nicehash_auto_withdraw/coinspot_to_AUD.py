import configparser
import time

import pushover_wrapper as pushover
from coinspot import CoinSpot

config = configparser.ConfigParser()
config.read('/config/config.ini')

pushover_client = pushover.Client(config['pushover']['user_key'], api_token=config['pushover']['api_token'])

pushover_client.send_message("Starting transfer from CoinSpot to AUD", title="Starting CoinSpot to AUD Transfer")

# initialise the library
client = CoinSpot(config['coinspot']['api_key'], config['coinspot']['api_secret'])

# get your coin wallet balances
balance = 0
try:
    balance = float(client.balances()['balance']['btc'])
except KeyError:
    pushover_client.send_message("CoinSpot confirmed balance: 0 BTC. Nothing to sell", title="CoinSpot Empty")
    exit(1)

pushover_client.send_message("CoinSpot confirmed balance: "+str(balance)+" BTC", title="CoinSpot Balance")

# Get a quote on buying a billion BTC, with estimation of timeframe
quote = client.quotesell('BTC', balance)['quote']
pushover_client.send_message("CoinSpot quoted "+str(quote)+" AUD/BTC for "+str(balance)+" BTC", title="CoinSpot Quote")

if config['coinspot'].getboolean('dry_run'):
    pushover_client.send_message("Dry run complete. No actions have been taken", title="CoinSpot Dry Run Complete")
    exit(0)

client.sell('BTC', balance, quote)

time.sleep(30)

try:
    aud_balance = float(client.balances()['balance']['aud'])
except KeyError:
    aud_balance = 0

pushover_client.send_message("Sale complete. "+str(aud_balance)+" AUD ready to be withdrawn from CoinSpot", title="CoinSpot Sale Compleate")
