#!/bin/bash

source $HOME/.pushbullet_vars
PROJECT_DIR=$(dirname $(readlink --canonicalize $0))

LOGFILE="$PROJECT_DIR/monitor.log"
DIR_PUSHBULLET_RESP="$PROJECT_DIR/pushbullet-log"

CHANGE='Page changed'
NO_CHANGE='No change'

function write_log() {
    echo "[ $(date -Iminutes) ] $1: $2" >> $LOGFILE
}

function alert_phone() {
    # OUTPUT='/dev/null'

    OUTPUT="$DIR_PUSHBULLET_RESP/$(date -Iminutes).json"
    if [ ! -d $DIR_PUSHBULLET_RESP ]
    then
        mkdir $DIR_PUSHBULLET_RESP
    fi

    curl --silent --output $OUTPUT \
        --request POST 'https://api.pushbullet.com/v2/pushes' \
        --header "Access-Token: $PUSHBULLET_TOKEN" \
        --form "device_iden=$PUSHBULLET_PHONE" \
        --form 'type=note' \
        --form 'title=LA Public Health Update' \
        --form "body=$1"

    write_log 'Pushbullet API' "$1"
}
