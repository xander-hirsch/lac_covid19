#!/bin/sh

DIR_DATA="./docs";
FILE_DATA_EXPORT="lac_covid19_data.zip"

cd $DIR_DATA;
zip $FILE_DATA_EXPORT *.csv && mv $FILE_DATA_EXPORT $WINDOWS_DOWNLOADS;