#!/bin/bash

cp $RECIPE_DIR/stocks-dashboard.py $PREFIX/bin

if [ `uname` == Darwin ]
then
    cp $RECIPE_DIR/stocks_dashboard.command $PREFIX/bin
fi

