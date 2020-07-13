curl --silent --output /dev/null \
    --request POST 'https://api.pushbullet.com/v2/pushes' \
    --header "Access-Token: $PUSHBULLET_TOKEN" \
    --form "device_iden=$PUSHBULLET_PHONE" \
    --form 'type=note' \
    --form 'title=LA Public Health Update' \
    --form "body=$1"
