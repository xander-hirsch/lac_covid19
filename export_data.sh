#!/bin/bash

DIR_DATA='./export'
ZIP_FILENAME='lac-covid19-data'
FILE_DATA_EXPORT="$ZIP_FILENAME.zip"

cd $DIR_DATA

zip -r $FILE_DATA_EXPORT . \
    && mv $FILE_DATA_EXPORT $W10_DATA \
    && rm -rf "$W10_DATA/$ZIP_FILENAME"
