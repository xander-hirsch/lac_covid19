#!/bin/bash

PROJECT_DIR=$(dirname $(readlink --canonicalize $0))
DATE_TARGET="$PROJECT_DIR/target-date.txt"
PREVIOUS_HTML="$PROJECT_DIR/pr-listing-previous.html"
CURRENT_HTML="$PROJECT_DIR/pr-listing-current.html"

TOMORROW='tomorrow'
LYNX_OPTS='-dump -nonumbers -nolist'

cd $PROJECT_DIR

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

if [ $old_hash != $new_hash ]
then
    ./alert-phone.sh 'New Press Release'
    mv $CURRENT_HTML $PREVIOUS_HTML
else
    rm $CURRENT_HTML
    echo "No changes"
fi
