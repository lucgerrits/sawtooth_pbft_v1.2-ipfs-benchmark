#!/bin/bash

docker-compose -f docker-compose.yaml down
docker-compose -f docker-compose-sender.yaml down

# VALIDATORDATAPATH="./sawtooth-data/validator-data/"
# VALIDATORDATAPATH="/media/100GB/validator-data"

#use env:
export $(grep -v '^#' .env | xargs -d '\n')

echo "Delete validator data"
du -sh "$VALIDATORDATAPATH"
rm -rf "$VALIDATORDATAPATH"
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


