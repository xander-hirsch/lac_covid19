#!/bin/sh

WIN_HTML=$LACHTML;
HTML_PAGE="./docs/index.html";
cp $WIN_HTML $HTML_PAGE && rm $WIN_HTML;
chmod 644 $HTML_PAGE;
