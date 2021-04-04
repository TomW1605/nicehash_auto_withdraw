import nicehash
import coinbase_to_coinspot
import coinspot
import configparser
from pushover import Client

config = configparser.ConfigParser()
config.read('config.ini')

pushover_client = Client(config['pushover']['user_key'], api_token=config['pushover']['api_token'])
pushover_client.send_message("Hello!", title="Hello")

'''nicehash_api = nicehash.private_api(config['nicehash']['host'], config['nicehash']['organisation_id'], config['nicehash']['api_key'], config['nicehash']['api_secret'], config['nicehash'].getboolean('verbose'))
nicehash_sent = nicehash_api.send_all(config['nicehash']['destination_address'], config['nicehash'].getboolean('dry_run'))

coinspot_client = coinspot.CoinSpot(config['coinspot']['api_key'], config['coinspot']['api_secret'])
coinspot_AUD_ammount = coinspot_client.sell_all(config['coinspot'].getboolean('dry_run'))'''
