#!/bin/sh

echo "Trapping kill signal"
trap "echo TRAPed signal" 1 2 3 15

echo "Placing config in mount"
cp -n /nicehash_auto_withdraw/config.default.ini /config/config.ini
chown -R 1000:1000 /config
chmod -R 777 /config

/etc/init.d/atd start

python3 /nicehash_auto_withdraw/nicehash_to_coinspot.py

echo "[hit enter key to exit] or run 'docker stop <container>'"
read varname

/etc/init.d/atd stop

echo "exited $0"