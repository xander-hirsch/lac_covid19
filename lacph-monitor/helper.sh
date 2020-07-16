#!/bin/bash

source $HOME/.pushbullet_vars
PROJECT_DIR=$(dirname $(readlink --canonicalize $0))

LOGFILE="$PROJECT_DIR/monitor.log"
DIR_PUSHBULLET_RESP="$PROJECT_DIR/pushbullet-log"

SUSPEND_FILE='.suspend_'

CHANGE='Page changed'
NO_CHANGE='No change'

function suspend_monitor() {
    touch $1
}

function check_monitor() {
    if [ -f $1 ]
    then
        exit
    fi
}

LYNX_OPTS='-dump -nonumbers -nolist -display_charset=utf-8'
function request_page() {
    lynx $LYNX_OPTS $1 > $2
}

function cli_opts() {
    # 1 - cli argument; 2 - URL; 3 - save file; 4 - suspend file
    msg=
    case $1 in
        'init')
            request_page $2 $3
            msg='Monitor initialized'
            ;;
        'suspend')
            suspend_monitor $4
            msg='Monitor suspended'
            ;;
        'reset')
            rm $4
            msg='Monitor reset'
            ;;
        *)
            msg='Bad option'
    esac
    echo "$msg"
    exit
}

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
