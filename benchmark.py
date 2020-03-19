#!/usr/bin/env python3.7


import subprocess
import datetime
import time
import pathlib
##################### CONFIG #####################

file_sender_log = "sender_log.log"
file_stats_log = "stats_log.log"

##################### DEF GENERAL #####################


def log(_str, ts=True, end="\n"):
    now = datetime.datetime.now()
    if ts:
        print("{} | {}".format(now.strftime("%Y-%m-%d %H:%M:%S"), _str), end=end)
    else:
        print("{}".format(_str), end=end)


def clear_file(filename):
    text_file = open(filename, "w")
    text_file.write("")
    text_file.close()


def append_file(filename, text):
    text_file = open(filename, "a")
    text_file.write(text)
    text_file.close()


def duplicate_file(filename, newfilename):
    filedata = None
    f = open(filename, 'r')
    filedata = f.read()
    f.close()

    f = open(newfilename, 'w')
    f.write(filedata)
    f.close()


def set_file_params(filename, marker, data):
    filedata = None
    f = open(filename, 'r')
    filedata = f.read()
    f.close()

    newdata = filedata.replace(marker, data)

    f = open(filename, 'w')
    f.write(newdata)
    f.close()


##################### DEF RUN SCRIPTS #####################


def start_blockchain(sawtooth_parameters):
    log("Start blockchain")

    log("Set parameters", end="")
    duplicate_file("docker-compose.yaml", "docker-compose.yaml.benchmark")
    set_file_params("docker-compose.yaml.benchmark",
                    "<BLOCKCHAIN_OPTIONS_max_batches_per_block>", sawtooth_parameters["max_batches_per_block"])
    set_file_params("docker-compose.yaml.benchmark",
                    "<BLOCKCHAIN_OPTIONS_block_publishing_delay>", sawtooth_parameters["block_publishing_delay"])
    set_file_params("docker-compose.yaml.benchmark",
                    "<BLOCKCHAIN_OPTIONS_idle_timeout>", sawtooth_parameters["idle_timeout"])
    set_file_params("docker-compose.yaml.benchmark",
                    "<BLOCKCHAIN_OPTIONS_forced_view_change_interval>", sawtooth_parameters["forced_view_change_interval"])
    set_file_params("docker-compose.yaml.benchmark",
                    "<BLOCKCHAIN_OPTIONS_commit_timeout>", sawtooth_parameters["commit_timeout"])
    set_file_params("docker-compose.yaml.benchmark",
                    "<BLOCKCHAIN_OPTIONS_view_change_duration>", sawtooth_parameters["view_change_duration"])
    log(" OK", ts=False)

    result = subprocess.check_output(
        ['docker-compose', '-f', 'docker-compose.yaml.benchmark', 'up', '-d', '--no-color', '--quiet-pull'], stderr=subprocess.STDOUT)
    log(result.decode("utf-8"), ts=False)
    log("Sleep {} sec for blockchain to start".format(10))
    time.sleep(10)


def start_influx_grafana():
    log("Start only influx and grafana")

    result = subprocess.check_output(
        ['docker-compose', '-f', 'docker-compose.yaml.benchmark', 'up', '-d', '--no-color', '--quiet-pull', 'grafana', 'influxdb'], stderr=subprocess.STDOUT)
    log(result.decode("utf-8"), ts=False)


def reset_blockchain():
    log("Reset blockchain")
    result = subprocess.check_output(['./reset.sh'], stderr=subprocess.STDOUT)
    log(result.decode("utf-8"), ts=False)
    log("Sleep {} sec for blockchain to stop".format(5))
    time.sleep(5)


def start_sender(sender_parameters, test_name):
    log("Start sender")

    log("Set parameters", end="")
    duplicate_file("docker-compose-sender.yaml",
                   "docker-compose-sender.yaml.benchmark")
    # params = "{} {} {}".format(
    #     sender_parameters["limit"], sender_parameters["js_nb_parallele"], sender_parameters["js_wait_time"])
    # set_file_params("docker-compose-sender.yaml.benchmark",
    #                 "<SENDER_TEST_OPTIONS>", params)
    # log(" OK", ts=False)

    # result = subprocess.check_output(
    #     ['docker-compose', '-f', 'docker-compose-sender.yaml.benchmark', 'up', 'sender'], stderr=subprocess.STDOUT)

    params = "{} {} {}".format(
        sender_parameters["js_nb_parallele"], sender_parameters["js_wait_time"], sender_parameters["limit"])
    set_file_params("docker-compose-sender.yaml.benchmark",
                    "<SENDER_TEST_JS_OPTIONS>", params)
    log(" OK", ts=False)

    result = subprocess.check_output(
        ['docker-compose', '-f', 'docker-compose-sender.yaml.benchmark', 'up', '--no-color', '--quiet-pull', 'sender-js'], stderr=subprocess.STDOUT)

    log(result.decode("utf-8"), ts=False)
    append_file(file_sender_log,
                "\n============= {} ============\n".format(test_name))
    # append_file(file_sender_log, result.decode("utf-8").split("Start loop")[1])
    append_file(file_sender_log, result.decode("utf-8"))
    append_file(file_sender_log,
                "\n============= END {} ============\n".format(test_name))
    log("Sleep {} sec for blockchain stabilize".format(20))
    time.sleep(20)


def start_stats(test_name):
    log("Start stats")
    working_dir = pathlib.Path(__file__).parent.absolute() / 'sender'
    result = subprocess.check_output(
        ['python3.7', 'test_links.py'], cwd=working_dir, stderr=subprocess.STDOUT)
    log(result.decode("utf-8"), ts=False)
    append_file(file_stats_log,
                "\n============= {} ============\n".format(test_name))
    append_file(file_stats_log, result.decode("utf-8"))
    append_file(file_stats_log,
                "\n============= END {} ============\n".format(test_name))
    time.sleep(1)

##################### MAIN #####################


def main(profiles):
    log("Start benchmark Hyperledger Sawtooth PBFT consensus")
    nb_profiles = len(profiles)
    log("Found {} benchmarks".format(nb_profiles))

    log("Clear {}".format(file_sender_log))
    clear_file(file_sender_log)
    log("Clear {}".format(file_stats_log))
    clear_file(file_stats_log)

    for i in range(nb_profiles):
        log("Benchmark n°{}".format(i))

        reset_blockchain()

        start_blockchain(profiles[i]["sawtooth_parameters"])

        start_sender(profiles[i]["sender_parameters"], "TEST n°{}".format(i))

        start_stats("TEST n°{}".format(i))

    log("Finishing")
    reset_blockchain()
    start_influx_grafana()

    log("Done {} benchmarks".format(nb_profiles))


# config doc: https://sawtooth.hyperledger.org/docs/pbft/nightly/master/configuring-pbft.html
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
    # {  # basic test first
    #     "sawtooth_parameters": {
    #         "max_batches_per_block": "100",
    #         "block_publishing_delay": "1000",
    #         "idle_timeout": "30000",
    #         "forced_view_change_interval": "100",
    #         "view_change_duration": "5000",
    #         "commit_timeout": "10000"
    #     },
    #     "sender_parameters": {
    #         "limit": "1000",
    #         "js_nb_parallele": "10",
    #         "js_wait_time": "3"
    #     }
    # },
    # {
    #     "sawtooth_parameters": {
    #         "max_batches_per_block": "100",
    #         "block_publishing_delay": "1000",
    #         "idle_timeout": "30000",
    #         "forced_view_change_interval": "100",
    #         "view_change_duration": "5000",
    #         "commit_timeout": "10000"
    #     },
    #     "sender_parameters": {
    #         "limit": "5000",
    #         "js_nb_parallele": "3",
    #         "js_wait_time": "1"
    #     }
    # },
    # {
    #     "sawtooth_parameters": {
    #         "max_batches_per_block": "100",
    #         "block_publishing_delay": "1000",
    #         "idle_timeout": "30000",
    #         "forced_view_change_interval": "100",
    #         "view_change_duration": "5000",
    #         "commit_timeout": "10000"
    #     },
    #     "sender_parameters": {
    #         "limit": "10000",
    #         "js_nb_parallele": "300",
    #         "js_wait_time": "100"
    #     }
    # },
    # {
    #     "sawtooth_parameters": {
    #         "max_batches_per_block": "200",
    #         "block_publishing_delay": "1000",
    #         "idle_timeout": "30000",
    #         "forced_view_change_interval": "100",
    #         "view_change_duration": "5000",
    #         "commit_timeout": "10000"
    #     },
    #     "sender_parameters": {
    #         "limit": "10000",
    #         "js_nb_parallele": "300",
    #         "js_wait_time": "100"
    #     }
    # },
    # {
    #     "sawtooth_parameters": {
    #         "max_batches_per_block": "500",
    #         "block_publishing_delay": "1000",
    #         "idle_timeout": "30000",
    #         "forced_view_change_interval": "100",
    #         "view_change_duration": "5000",
    #         "commit_timeout": "10000"
    #     },
    #     "sender_parameters": {
    #         "limit": "10000",
    #         "js_nb_parallele": "3",
    #         "js_wait_time": "1"
    #     }
    # },
    # {
    #     "sawtooth_parameters": {
    #         "max_batches_per_block": "1000",
    #         "block_publishing_delay": "1000",
    #         "idle_timeout": "30000",
    #         "forced_view_change_interval": "100",
    #         "view_change_duration": "5000",
    #         "commit_timeout": "10000"
    #     },
    #     "sender_parameters": {
    #         "limit": "10000",
    #         "js_nb_parallele": "3",
    #         "js_wait_time": "1"
    #     }
    # },
    # {
    #     "sawtooth_parameters": {
    #         "max_batches_per_block": "500",
    #         "block_publishing_delay": "1000",
    #         "idle_timeout": "30000",
    #         "forced_view_change_interval": "100",
    #         "view_change_duration": "5000",
    #         "commit_timeout": "10000"
    #     },
    #     "sender_parameters": {
    #         "limit": "10000",
    #         "js_nb_parallele": "3",
    #         "js_wait_time": "5"
    #     }
    # },
    # {
    #     "sawtooth_parameters": {
    #         "max_batches_per_block": "500",
    #         "block_publishing_delay": "1000",
    #         "idle_timeout": "30000",
    #         "forced_view_change_interval": "5",
    #         "view_change_duration": "5000",
    #         "commit_timeout": "10000"
    #     },
    #     "sender_parameters": {
    #         "limit": "10000",
    #         "js_nb_parallele": "3",
    #         "js_wait_time": "1"
    #     }
    # },
    # {
    #     "sawtooth_parameters": {
    #         "max_batches_per_block": "500",
    #         "block_publishing_delay": "1000",
    #         "idle_timeout": "30000",
    #         "forced_view_change_interval": "50",
    #         "view_change_duration": "5000",
    #         "commit_timeout": "10000"
    #     },
    #     "sender_parameters": {
    #         "limit": "10000",
    #         "js_nb_parallele": "3",
    #         "js_wait_time": "1"
    #     }
    # },
    # {
    #     "sawtooth_parameters": {
    #         "max_batches_per_block": "500",
    #         "block_publishing_delay": "1000",
    #         "idle_timeout": "30000",
    #         "forced_view_change_interval": "500",
    #         "view_change_duration": "5000",
    #         "commit_timeout": "10000"
    #     },
    #     "sender_parameters": {
    #         "limit": "10000",
    #         "js_nb_parallele": "3",
    #         "js_wait_time": "1"
    #     }
    # },
    # {
    #     "sawtooth_parameters": {
    #         "max_batches_per_block": "500",
    #         "block_publishing_delay": "1000",
    #         "idle_timeout": "30000",
    #         "forced_view_change_interval": "100",
    #         "view_change_duration": "5000",
    #         "commit_timeout": "10000"
    #     },
    #     "sender_parameters": {
    #         "limit": "10000",
    #         "js_nb_parallele": "3",
    #         "js_wait_time": "1"
    #     }
    # },
    # {
    #     "sawtooth_parameters": {
    #         "max_batches_per_block": "500",
    #         "block_publishing_delay": "2000",
    #         "idle_timeout": "60000",
    #         "forced_view_change_interval": "200",
    #         "view_change_duration": "10000",
    #         "commit_timeout": "20000"
    #     },
    #     "sender_parameters": {
    #         "limit": "10000",
    #         "js_nb_parallele": "3",
    #         "js_wait_time": "1"
    #     }
    # },
]
main(test_profiles)
