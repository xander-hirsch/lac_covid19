#!/bin/sh

IPYNB_NAME="lacph_graphs"
W10_HTML="$W10_DOWNLOADS/$IPYNB_NAME.html";
HTML_PAGE="./docs/index.html";

# jupyter notebook $LAC_IPYNB;

cp $W10_HTML $HTML_PAGE && rm $W10_HTML;
chmod 644 $HTML_PAGE;

git add $HTML_PAGE;
