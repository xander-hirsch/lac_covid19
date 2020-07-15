#!/bin/bash

IPYNB_NAME='lacph_graphs'
W10_HTML="$W10_DOWNLOADS/$IPYNB_NAME.html"
REPO_HTML='./docs/index.html'

jupyter notebook "data_viz/$IPYNB_NAME.ipynb"

if [ $W10_HTML -nt $REPO_HTML ]
then
    mv $W10_HTML $REPO_HTML && chmod 644 $REPO_HTML
    ./data_viz/git_ipynb.sh
fi
