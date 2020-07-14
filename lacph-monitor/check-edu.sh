#!/bin/bash

PROJECT_DIR=$(dirname $(readlink --canonicalize $0))
source $PROJECT_DIR/helper.sh

SCHOOL_PDF='GuidanceSchoolAdministrators.pdf'
COLLEGE_PDF='GuidanceCollegesUniversities.pdf'

SCHOOL_SHA1='3db51b2c95ce045b8eae20a793621ca872f4fb30'
COLLEGE_SHA1='df95546baa42d42f01c728c3a43427c40d2ca1e8'

BASE_URL='http://publichealth.lacounty.gov/media/Coronavirus/docs/education'
SCHOOL_URL="${BASE_URL}/${SCHOOL_PDF}"
COLLEGE_URL="${BASE_URL}/${COLLEGE_PDF}"

RESP_FLAG='--silent'

check_for_change() {
    # First arg is file, Second arg is original hash, Third arg is name
    file_hash=($(sha1sum $1))
    logreport=$NO_CHANGE

    if [ $file_hash != $2 ]
    then
        ./alert-phone.sh "Guidance update for $3"
        logreport=$CHANGE
    fi

    write_log $3 "$logreport"
}

cd $PROJECT_DIR

curl $RESP_FLAG -o $SCHOOL_PDF $SCHOOL_URL
curl $RESP_FLAG -o $COLLEGE_PDF $COLLEGE_URL

check_for_change $SCHOOL_PDF $SCHOOL_SHA1 'K-12'
check_for_change $COLLEGE_PDF $COLLEGE_SHA1 'Colleges'
