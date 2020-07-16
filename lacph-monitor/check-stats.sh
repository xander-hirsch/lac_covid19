#!/bin/bash

cd $(dirname $(readlink --canonicalize $0))
source helper.sh

SUSPEND_STATS="${SUSPEND_FILE}stats"

STATS_URL='http://publichealth.lacounty.gov/media/Coronavirus/locations.htm'
OLD_STATS='case-summary.txt'
NEW_STATS="$OLD_STATS.tmp"

if [ $# -eq 1 ]
then
    cli_opts $1 $STATS_URL $OLD_STATS $SUSPEND_STATS
fi

check_monitor $SUSPEND_STATS

request_page $STATS_URL $NEW_STATS

old_hash=($(sha1sum $OLD_STATS))
new_hash=($(sha1sum $NEW_STATS))

logreport=$NO_CHANGE

if [ $old_hash != $new_hash ]
then
    mv $NEW_STATS $OLD_STATS
    logreport=$CHANGE
    alert_phone 'Case statistics'
    suspend_monitor $SUSPEND_STATS
else
    rm $NEW_STATS
fi

write_log 'Case Summary' "$logreport"
