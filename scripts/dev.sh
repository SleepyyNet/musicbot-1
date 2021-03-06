#!/bin/bash

my_dir="$(dirname "$0")"
export AIOCACHE_DISABLE=1
export MB_DATABASE=musicbot_prod
export MB_NO_AUTH=1

while true; do
    $my_dir/../env/bin/python $my_dir/../musicbot --verbosity debug server --dev --autoscan start --http-server dev.musicbot.ovh --http-host 127.0.0.1 --http-port 1337 --http-user musicbot --http-password musicbot
    sleep 1;
done
