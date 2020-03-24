# Benchmark for Sawtooth (PBFT consensus)

Benchmark for Sawtooth with PBFT consensus, embedded into a docker-compose and python script. 

Contains: 

* Sawtooth with PBFT consensus
* stccpp (C++)
* sender tool using stcpp
* IPFS (module files etc)
  
Requires:

* docker & docker-compose
* python 3.7

## Build

Build to copy and set all the necessary files in the project.
```bash
./build.sh
```

## Benchmark config

Configure benchmark inside of ./benchmark.py . 

Each profile is a test and uses docker-compose.yaml & docker-compose-sender.yaml as a template to create docker-compose.yaml.benchmark & docker-compose-sender.yaml.benchmark. 

For example:

```python
test_profiles = [
    {  # basic test first
        "sawtooth_parameters": {
            "max_batches_per_block": "300",
            "block_publishing_delay": "1000",
            "idle_timeout": "30000",
            "forced_view_change_interval": "100",
            "view_change_duration": "5000",
            "commit_timeout": "5000"
        },
        "sender_parameters": {
            "limit": "10000",
            "js_nb_parallele": "3",
            "js_wait_time": "1"
        }
    },
    #{
    #...
    #}
}
```


The location of the validator data is **by default on an separate HDD** to avoid filling the main drive. 
Set dot env variable it before continuing:

In .env :
```bash
VALIDATORDATAPATH=/media/100GB/validator-data
```


## Start benchmark

Please read the config section before starting the benchmark !
```bash
./benchmark.py
```
This will execute each profile of tests set in ./benchmark.py .

Note: At the end, benchmark.py **finish by starting grafana and influxdb.**

## Reset benchmark

Stop all containers and delete all data.

```bash
./reset.py
```


