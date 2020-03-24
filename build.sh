#!/bin/bash

# VALIDATORDATAPATH="$VALIDATORDATAPATH/"
# VALIDATORDATAPATH="/media/100GB/validator-data"

#use env:
export $(grep -v '^#' .env | xargs -d '\n')

do_build () {
    if [ ! -d ./sawtooth-sdk-python ]; then
        echo -n "Can't find sawtooth-sdk-python"
        echo "=> Cloning project"
        git clone https://github.com/hyperledger/sawtooth-sdk-python.git
        echo "Done"
    fi

    echo -n "Adding cartp files in sawtooth-sdk-python"
    cp -rf ./cartp-data/bin/cartp-tp-python ./sawtooth-sdk-python/bin/
    echo -n " ="
    cp -rf ./cartp-data/cartp_python ./sawtooth-sdk-python/examples/
    #module ipfs:
    echo -n " ="
    cp -rf ./moduleipfs-data/IPFS_Module ./sawtooth-sdk-python/examples/
    echo " => OK"

    echo "Delete validator data"
    if [ ! -d $VALIDATORDATAPATH ]; then
        du -sh $VALIDATORDATAPATH
    fi
    rm -rf $VALIDATORDATAPATH
    rm -rf ./sawtooth-data/pbft-shared
    echo "Done"

    echo "make validator data dir"
    mkdir -p $VALIDATORDATAPATH
    mkdir -p $VALIDATORDATAPATH/v0
    mkdir -p $VALIDATORDATAPATH/v1
    mkdir -p $VALIDATORDATAPATH/v2
    mkdir -p $VALIDATORDATAPATH/v3
    mkdir -p $VALIDATORDATAPATH/v4
    mkdir -p ./sawtooth-data/pbft-shared
    echo "Done"


    sudo chown 104:104 -R ./stats-data/grafana-data
}



read -p "Are you sure to build (overwrite) cartp into sawtooth-sdk-python? [Yy]" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "===================Start======================"
    do_build
    echo "===================Done======================"
else
    echo "===================Stop======================"
fi
