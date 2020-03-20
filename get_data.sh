

START_TS="$1"
END_TS="$2"

interval="1s"
timeFilter="time >= "$START_TS"ms and time <= "$END_TS"ms"

#get exec time:
CMD="influx -username lrdata -password lrdata -database 'metrics' -execute '" 
CMD+="SELECT non_negative_derivative(last("count"), 10s) /10 AS \"rate\" \
FROM \"sawtooth_validator.executor.TransactionExecutorThread.transaction_execution_count\" \
WHERE $timeFilter GROUP BY time($interval), \"host\" fill(linear) "
CMD+="' -format csv"

#get reject rate:
# CMD="influx -username lrdata -password lrdata -database 'metrics' -execute '" 
# CMD+="SELECT moving_average(non_negative_derivative(mean(\"value\"), 10s), 5)  / 10 AS \"rate\" \
# FROM \"sawtooth_validator.back_pressure_handlers.ClientBatchSubmitBackpressureHandler.backpressure_batches_rejected_gauge\" \
# WHERE $timeFilter GROUP BY time($interval) fill(previous) "
# CMD+="' -format csv"

#get tx rate:
# CMD="influx -username lrdata -password lrdata -database 'metrics' -execute '" 
# CMD+="SELECT moving_average(non_negative_derivative(mean(\"value\"), 10s), 30)  / 10 AS \"rate\" \
# FROM \"sawtooth_validator.chain.ChainController.committed_transactions_gauge\" \
# WHERE $timeFilter GROUP BY time($interval) fill(previous) "
# CMD+="' -format csv"

echo $CMD
docker exec -it influxdb bash -c "$CMD" > data.csv