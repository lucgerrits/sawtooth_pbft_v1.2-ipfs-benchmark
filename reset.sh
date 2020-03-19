#!/bin/bash

docker-compose -f docker-compose.yaml down
docker-compose -f docker-compose-sender.yaml down

# validatordatapath="./sawtooth-data/validator-data/"
validatordatapath="/media/100GB/validator-data"

echo "Delete validator data"
du -sh "$validatordatapath"
rm -rf "$validatordatapath"
rm -rf ./sawtooth-data/pbft-shared
echo "Done"

echo "make validator data dir"
mkdir -p $validatordatapath
mkdir -p $validatordatapath/v0
mkdir -p $validatordatapath/v1
mkdir -p $validatordatapath/v2
mkdir -p $validatordatapath/v3
mkdir -p $validatordatapath/v4
mkdir -p ./sawtooth-data/pbft-shared
echo "Done"


