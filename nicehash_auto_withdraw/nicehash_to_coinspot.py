import configparser

import nicehash
import pushover_wrapper as pushover

config = configparser.ConfigParser()
config.read('config.ini')

pushover_client = pushover.Client(config['pushover']['user_key'], api_token=config['pushover']['api_token'])

private_api = nicehash.private_api(config['nicehash']['host'],
                                   config['nicehash']['organisation_id'],
                                   config['nicehash']['api_key'],
                                   config['nicehash']['api_secret'],
                                   config['nicehash'].getboolean('verbose'))

my_btc_account = private_api.get_accounts_for_currency("BTC")

nh_balance = float(my_btc_account['available'])
# print(nh_balance)
pushover_client.send_message("Nicehash confirmed balance: "+str(nh_balance)+" BTC", title="Nicehash Balance")

if nh_balance > config['nicehash'].getfloat('transfer_limit'):
    withdrawal_addresses = private_api.get_withdrawal_addresses('BTC', 100, 0)
    # print(withdrawal_addresses)

    destination_id = ""
    for wa in withdrawal_addresses['list']:
        # print(wa['address'])
        if wa['address'] == config['nicehash']['destination_address']:
            destination_id = wa['id']
            break

    if destination_id != "":
        pushover_client.send_message("Transferring "+str(nh_balance)+" BTC, to crypto account: "+config['nicehash']['destination_address'], title="Nicehash Transfer")
        if config['nicehash'].getboolean('dry_run'):
            pushover_client.send_message("Dry run complete. No actions have been taken", title="Nicehash Dry Run Complete")

        res = private_api.withdraw_request(destination_id, nh_balance, 'BTC')

        if res['status_code'] == 200:
            pushover_client.send_message("Transfer complete. Please allow 24 hours for BTC to appear in Coinspot account", title="Nicehash Transfer Complete")
        else:
            pushover_client.send_message("Transfer failed with error "+str(res["errors"][0]["code"])+": "+res["errors"][0]["message"]+". Retrying in "+str(config['nicehash']["retry_interval"])+" days", title="Nicehash Transfer Failed")

