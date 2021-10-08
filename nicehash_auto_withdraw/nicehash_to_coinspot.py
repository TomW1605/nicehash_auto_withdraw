import configparser
import datetime
import math

import nicehash
import pushover_wrapper as pushover
from atd import atd

config = configparser.ConfigParser()
config.read('/config/config.ini')

pushover_client = pushover.Client(config['pushover']['user_key'], api_token=config['pushover']['api_token'])

pushover_client.send_message("Starting transfer from NiceHash to CoinSpot", title="Starting NiceHash to CoinSpot Transfer")

atd.clear()
next_run_date = (datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)+datetime.timedelta(days=32)).replace(day=1)
backup_job = atd.at("python3 /nicehash_auto_withdraw/nicehash_to_coinspot.py", next_run_date)
pushover_client.send_message("Set backup job in case of crash", title="Backup Job")

private_api = nicehash.private_api(config['nicehash']['host'],
                                   config['nicehash']['organisation_id'],
                                   config['nicehash']['api_key'],
                                   config['nicehash']['api_secret'],
                                   config['nicehash'].getboolean('verbose'))

my_btc_account = private_api.get_accounts_for_currency("BTC")

nh_balance = float(my_btc_account['available'])
# print(nh_balance)
pushover_client.send_message("NiceHash confirmed balance: "+str(nh_balance)+" BTC", title="NiceHash Balance")

next_run = 30
success = False

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
            pushover_client.send_message("Dry run complete. No actions have been taken", title="NiceHash Dry Run Complete")
            exit(0)

        res = private_api.withdraw_request(destination_id, nh_balance, 'BTC')

        if res['status_code'] == 200:
            pushover_client.send_message("Transfer complete. Please allow 24 hours for BTC to appear in Coinspot account", title="NiceHash Transfer Complete")
            success = True
        else:
            pushover_client.send_message("Transfer failed with error "+str(res["errors"][0]["code"])+": "+res["errors"][0]["message"]+". Retrying in "+str(config['nicehash']["retry_interval"])+" days", title="Nicehash Transfer Failed")
            next_run = config['nicehash']["retry_interval"]
else:
    profitability = private_api.get_mining_rigs()['totalProfitability']
    btc_remaining = config['nicehash'].getfloat('transfer_limit')-nh_balance

    if profitability == 0:
        days_remaining = config['nicehash']["retry_interval"]
    else:
        days_remaining = math.ceil(btc_remaining/profitability)

    if days_remaining > 30:
        days_remaining = config['nicehash']["retry_interval"]

    pushover_client.send_message("Transfer failed, insufficient funds. Retrying in "+str(days_remaining)+" days", title="Nicehash Transfer Failed")
    next_run = days_remaining

if success:
    try:
        if config['nicehash'].getboolean('to_AUD'):
            atd.at("python3 /nicehash_auto_withdraw/coinspot_to_AUD.py", datetime.datetime.now()+datetime.timedelta(hours=12))
            pushover_client.send_message("Scheduled coinspot_to_AUD.py to run in 12 hours", title="Schedule coinspot_to_AUD.py")
    except KeyError:
        atd.at("python3 /nicehash_auto_withdraw/coinspot_to_AUD.py", datetime.datetime.now()+datetime.timedelta(hours=12))
        pushover_client.send_message("Scheduled coinspot_to_AUD.py to run in 12 hours", title="Schedule coinspot_to_AUD.py")

    next_run_date = (datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)+datetime.timedelta(days=32)).replace(day=1)
    atd.at("python3 /nicehash_auto_withdraw/nicehash_to_coinspot.py", next_run_date)
    pushover_client.send_message("Scheduled nicehash_to_coinspot.py to run on "+str(next_run_date), title="Schedule nicehash_to_coinspot.py")

    atd.atrm(backup_job)
else:
    next_run_date = (datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)+datetime.timedelta(days=next_run))
    if next_run_date.month > datetime.datetime.now().month:
        next_run_date = (datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)+datetime.timedelta(days=32)).replace(day=1)
    atd.at("python3 /nicehash_auto_withdraw/nicehash_to_coinspot.py", next_run_date)
    pushover_client.send_message("Scheduled nicehash_to_coinspot.py to run on "+str(next_run_date), title="Schedule nicehash_to_coinspot.py")

    atd.atrm(backup_job)
