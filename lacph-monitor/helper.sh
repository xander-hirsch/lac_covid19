#!/bin/bash

source $HOME/.pushbullet_vars
LOGFILE="$PROJECT_DIR/monitor.log"

CHANGE='Page changed'
NO_CHANGE='No change'

function alert_phone() {
    OUTPUT="$PROJECT_DIR/pushbullet-log/$(date -Iminutes).json"
    # OUTPUT='/dev/null'

    curl --silent --output $OUTPUT \
        --request POST 'https://api.pushbullet.com/v2/pushes' \
        --header "Access-Token: $PUSHBULLET_TOKEN" \
        --form "device_iden=$PUSHBULLET_PHONE" \
        --form 'type=note' \
        --form 'title=LA Public Health Update' \
        --form "body=$1"
}

function write_log() {
    echo "[ $(date -Iminutes) ] $1: $2" >> $LOGFILE
}
