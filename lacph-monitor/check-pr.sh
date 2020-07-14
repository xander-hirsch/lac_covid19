#!/bin/bash

PROJECT_DIR=$(dirname $(readlink --canonicalize $0))
source $PROJECT_DIR/helper.sh

LOG_NAME='Press Release'
ALERT_MSG='New press release'

DATE_TARGET="$PROJECT_DIR/target-date.txt"
PREVIOUS_HTML="$PROJECT_DIR/pr-listing-previous.html"
CURRENT_HTML="$PROJECT_DIR/pr-listing-current.html"

TOMORROW='tomorrow'
LYNX_OPTS='-dump -nonumbers -nolist'

request_page() {
    curl --compressed --silent \
        --header 'Accept: text/html' \
        --header 'Accept-Language: en-US' \
        --output $1 \
        'http://publichealth.lacounty.gov/phcommon/public/media/mediaCOVIDdisplay.cfm'
}

monitor_suspend() {
    date -I --date=$TOMORROW > $DATE_TARGET
    echo 'LACPH press release monitor suspeneded until tomorrow'
    exit

}

monitor_reset() {
    date -I > $DATE_TARGET
    echo 'LACPH press release monitor reset'
}

initialize() {
    request_page $PREVIOUS_HTML
    date -I > $DATE_TARGET
    echo 'LACPH monitor initalized'
    exit
}

cd $PROJECT_DIR

# Stop checking until tomorrow or reset
if [ $# -eq 1 ]
then
    case $1 in
        "suspend")
            monitor_suspend
            ;;
        "reset")
            monitor_reset
            ;;
        "initialize")
            initialize
            ;;
        *)
            echo "Bad option"
            exit
            ;;
    esac
fi

# Halt if target date is not today
if [ $(date -I) != $(cat $DATE_TARGET) ]
then
    exit
fi

# Download and compute hashes
request_page $CURRENT_HTML

old_hash=($(lynx $LYNX_OPTS $PREVIOUS_HTML | sha1sum))
new_hash=($(lynx $LYNX_OPTS $CURRENT_HTML | sha1sum))

logreport=$NO_CHANGE

if [ $old_hash != $new_hash ]
then
    alert_phone "$ALERT_MSG"
    mv $CURRENT_HTML $PREVIOUS_HTML
    logreport=$CHANGE
else
    rm $CURRENT_HTML
fi

write_log "$LOG_NAME" "$logreport"
