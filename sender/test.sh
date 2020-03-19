#!/bin/bash

mode="js"
# limit=10000
# sleep_value=0.2
# send_init_tx=true
# js_nb_parallele=3
# js_wait_time=1

limit=$1
sleep_value=0.2
send_init_tx=true
js_nb_parallele=$2
js_wait_time=$3

apiURL="10.1.0.222:8080"
result_file="tmp.txt"

tnxprivatekey=$(<tests_keys/driver.priv)
tnxpublickey=$(<tests_keys/driver.pub)
batchprivatekey=$(<tests_keys/car.priv)
batchpublickey=$(<tests_keys/car.pub)

# echo "===================Config======================"
# echo "apiURL: $apiURL"
# echo "limit: $limit"
# echo "sleep_value: $sleep_value"
# echo "send_init_tx: $send_init_tx"
# echo "result_file: $result_file"
# echo "result_file: $result_file"
echo "======Start======"

send_new_car_transaction () {
    ./transaction --mode cartp \
        --tnxprivatekey $(<tests_keys/car.priv) \
        --tnxpublickey $(<tests_keys/car.pub) \
        --batchprivatekey $(<tests_keys/factory1.priv) \
        --batchpublickey $(<tests_keys/factory1.pub) \
        --cmd new_car \
        --car_brand "Kittmobile" \
        --car_type "Danger" \
        --car_licence "X1-102-10V" \
        --url "http://$apiURL/batches"
}

send_new_owner_transaction () {
    ./transaction --mode cartp \
        --tnxprivatekey $tnxprivatekey \
        --tnxpublickey $tnxpublickey \
        --batchprivatekey $batchprivatekey \
        --batchpublickey $batchpublickey \
        --cmd new_owner \
        --owner_lastname "Pikachou" \
        --owner_name "Mr. V" \
        --owner_address "1 av Atlantis" \
        --owner_country "France" \
        --url "http://$apiURL/batches"
}

index=1
errors=0
TX_OUTPUT=""
TX_RESULT=""
TX_LINK=""
send_crash_transaction () {
    TX_OUTPUT=$(./transaction --mode cartp \
        --tnxprivatekey $tnxprivatekey \
        --tnxpublickey $tnxpublickey \
        --batchprivatekey $batchprivatekey \
        --batchpublickey $batchpublickey \
        --cmd crash \
        --accident_ID "QmfM2r8seH2GiRaC4esTjeraXEachRt8ZsSeGaWTPLyMoG" \
        --signature $line \
        --dataPublicKey "Bxm4djh5ap9zBb9YyYHzdw5j6v8IOaHn" \
        --url "http://$apiURL/batches")

    echo -n "="
}

test_transaction () {
    TX_LINK=$(echo "$TX_OUTPUT" | grep -w "link")
    if [ -z "$TX_LINK" ]
    then
        #not ok
        TX_RESULT="error"
        errors=$(( $errors + 1 ))
        echo "Request: $TX_OUTPUT"
    else
        #ok
        TX_RESULT="ok"
    fi

    echo -n "="
}

get_transaction_id () {
    echo -ne "$TX_LINK" | grep -oP ': "\K[^"]+' >> "./$result_file"

    echo -n "="
}

finish () {
    elapsed="$(bc <<< "$ENDTIME - $STARTTIME")"

    echo "Done $limit elements"
    echo "Errors: $errors"
    echo "Time: $elapsed"
    echo "===================Stop======================"
}

# main_prog () {

if [ "$send_init_tx" = true ] ; then
    # echo "Sending initial TX"
    send_new_car_transaction
    send_new_owner_transaction
    # echo -n "Waiting 3 seconds to stabilize"
    sleep 3
# else
    # echo -n "Skip init transactions"
fi

# echo " => OK"


# echo -n "Delete $result_file"
rm -rf $result_file
# echo " => OK"


# echo "Start loop "

if [ "$mode" = "js" ] ; then
    # echo "Nodejs mode"
    sleep 2
    STARTTIME=$(date -u +%s.%N)
    #node test.js js_nb_parallele js_wait_time limit ....
    node test.js "$js_nb_parallele" "$js_wait_time" "$limit" "$tnxprivatekey" "$tnxpublickey" "$batchprivatekey" "$batchpublickey" "$apiURL"
    ENDTIME=$(date -u +%s.%N)
    elapsed="$(bc <<< "$ENDTIME - $STARTTIME")"
    echo "Done $limit elements"
    echo "Time: $elapsed"
else
    echo "Bash mode"
    sleep 2
    STARTTIME=$(date -u +%s.%N)
    while IFS= read -r line; do
        echo -n "$index:Sending "
        send_crash_transaction
        test_transaction
        get_transaction_id
        if [ $index -eq $limit ]
        then
            break
        fi
        echo -n "="
        index=$(( $index + 1 ))
        echo -n "="
        echo " => $TX_RESULT"
        sleep $sleep_value
    done < "signatures.sig"
    ENDTIME=$(date -u +%s.%N)
    finish
fi



# finish
# }

# ##############catch sigkill##############
# exit_script() {
#     echo "Stopping ..."

#     finish

#     trap - SIGINT SIGTERM # clear the trap
#     kill -- -$$ # Sends SIGTERM to child/sub processes
# }

# trap exit_script SIGINT SIGTERM


#############main code#######
# main_prog