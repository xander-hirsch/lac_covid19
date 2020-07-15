#!/bin/bash

PROJECT_DIR=$(dirname $(readlink --canonicalize $0))
source $PROJECT_DIR/helper.sh

PR_URL='http://publichealth.lacounty.gov/phcommon/public/media/mediaCOVIDdisplay.cfm'

LOG_NAME='Press Release'

DATE_TARGET="$PROJECT_DIR/target-date.txt"

PREVIOUS_TXT="$PROJECT_DIR/pr-listing-previous.txt"
CURRENT_TXT="$PROJECT_DIR/pr-listing-current.txt"
DIFF_TXT="$PROJECT_DIR/pr-listing-difference.txt"

TOMORROW='tomorrow'
LYNX_OPTS='-dump -nonumbers -nolist'

USUAL_STATS_TILE='[[:digit:],]+ New Deaths and [[:digit:],]+ New Cases'

request_page() {
    lynx $LYNX_OPTS $PR_URL > $1        
}

monitor_suspend() {
    date -I --date=$TOMORROW > $DATE_TARGET
    echo 'LACPH press release monitor suspeneded until tomorrow'

}

monitor_reset() {
    date -I > $DATE_TARGET
    echo 'LACPH press release monitor reset'
    exit
}

initialize() {
    request_page $PREVIOUS_TXT
    date -I > $DATE_TARGET
    echo 'LACPH monitor initalized'
    exit
}

cd $PROJECT_DIR

# Stop checking until tomorrow or reset
if [ $# -eq 1 ]
then
    case $1 in
        'suspend')
            monitor_suspend
            exit
            ;;
        'reset')
            monitor_reset
            ;;
        'initialize')
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

# Check the current page
request_page $CURRENT_TXT

# Calculate differences
diff --strip-trailing-cr $PREVIOUS_TXT $CURRENT_TXT > $DIFF_TXT
diff_exit=$?

logreport=$NO_CHANGE

if [ $diff_exit -eq 1 ]
then
    new_headline=$(sed -e '1d' -e 's/>\s\+//' $DIFF_TXT | tr '\n' ' ')
    new_headline=${new_headline/' View'}

    alert_phone "$new_headline"
    mv $CURRENT_TXT $PREVIOUS_TXT
    logreport=$CHANGE

    if echo $new_headline | grep -i -E "$USUAL_STATS_TITLE" > /dev/null
    then
        monitor_suspend > /dev/null
    fi
else
    rm $CURRENT_TXT
fi

rm $DIFF_TXT
write_log "$LOG_NAME" "$logreport"
