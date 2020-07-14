#!/bin/bash

source $HOME/.pushbullet_vars
cd $(dirname $(readlink --canonicalize $0))

OUTPUT="pushbullet-log/$(date -Iminutes)"
# OUTPUT='/dev/null'

curl --silent --output $OUTPUT \
    --request POST 'https://api.pushbullet.com/v2/pushes' \
    --header "Access-Token: $PUSHBULLET_TOKEN" \
    --form "device_iden=$PUSHBULLET_PHONE" \
    --form 'type=note' \
    --form 'title=LA Public Health Update' \
    --form "body=$1"
