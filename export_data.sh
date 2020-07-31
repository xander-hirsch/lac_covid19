#!/bin/bash

DIR_DATA='./append-data'
FOLDER_DATA_EXPORT='lac-covid19-data-append'
FILE_DATA_EXPORT="$FOLDER_DATA_EXPORT.zip"

cd $DIR_DATA

cp ../docs/{current,deltas}/*.csv .

# Change filename for ArcGIS compatability
mv region-deltas.csv delta-region.csv

zip $FILE_DATA_EXPORT *.csv \
    && mv $FILE_DATA_EXPORT $W10_DATA \
    && rm -rf "$W10_DATA/$FOLDER_DATA_EXPORT"
