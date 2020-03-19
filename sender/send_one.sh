#!/bin/bash

apiURL="10.1.0.222:8080"

tnxprivatekey=$(<tests_keys/driver.priv)
tnxpublickey=$(<tests_keys/driver.pub)
batchprivatekey=$(<tests_keys/car.priv)
batchpublickey=$(<tests_keys/car.pub)

./transaction  --mode cartp \
        --tnxprivatekey $tnxprivatekey \
        --tnxpublickey $tnxpublickey \
        --batchprivatekey $batchprivatekey \
        --batchpublickey $batchpublickey \
        --cmd crash \
        --accident_ID "QmfM2r8seH2GiRaC4esTjeraXEachRt8ZsSeGaWTPLyMoG" \
        --signature "88e19d9043e47b7318fbe2cf83e020da8e98f969b8d47ef50227f659b0d805f832dac88dbfb7639cc0019b6198fa439ed19e1f07de892e75eef5261c74b7e9b6" \
        --dataPublicKey "Bxm4djh5ap9zBb9YyYHzdw5j6v8IOaHn" \
        --url "http://$apiURL/batches"
