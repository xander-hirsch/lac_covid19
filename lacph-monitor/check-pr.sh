#!/bin/bash

cd $(dirname $(readlink --canonicalize $0))
source helper.sh

SUSPEND_PR="${SUSPEND_FILE}pr"

PR_URL='http://publichealth.lacounty.gov/phcommon/public/media/mediaCOVIDdisplay.cfm'
OLD_PR='pr-listing.txt'
NEW_PR="$OLD_PR.tmp"
DIFF_PR="$OLD_PR.diff"

LOG_NAME='Press Release'

USUAL_STATS_TILE='[[:digit:],]+ New Deaths and [[:digit:],]+ New Cases'

if [ $# -eq 1 ]
then
    cli_opts $1 $PR_URL $OLD_PR $SUSPEND_PR
fi

check_monitor $SUSPEND_PR

# Check the current page
request_page $PR_URL $NEW_PR

# Calculate differences
diff --strip-trailing-cr $OLD_PR $NEW_PR > $DIFF_PR
diff_exit=$?

logreport=$NO_CHANGE

if [ $diff_exit -eq 1 ]
then
    new_headline=$(sed -e '1d' -e 's/>\s\+//' $DIFF_PR | tr '\n' ' ')
    new_headline=${new_headline/' View'}

    alert_phone "$new_headline"
    mv $NEW_PR $OLD_PR
    logreport=$CHANGE

    if echo $new_headline | grep -i -E "$USUAL_STATS_TITLE" > /dev/null
    then
        suspend_monitor $SUSPEND_PR
    fi
else
    rm $NEW_PR
fi

rm $DIFF_PR
write_log "$LOG_NAME" "$logreport"
