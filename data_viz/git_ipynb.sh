#!/bin/bash

cd $(dirname $(readlink --canonicalize $0))

for ipynb in *.ipynb
do
    pyexport=$(echo $ipynb | sed 's/.ipynb/.py/')
    if [ $ipynb -nt $pyexport ]
    then
        jupyter nbconvert --to python $ipynb
    fi
done
