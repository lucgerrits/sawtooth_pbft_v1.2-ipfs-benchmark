var async = require("async");
var request = require("request");
const fs = require('fs');
const readline = require('readline');
const { spawn } = require('child_process');
var exec = require('child_process').exec;

const verbose = false;

const nb_batch_parallele = parseInt(process.argv[2]);
const waiting_time = parseFloat(process.argv[3]) * 1000;

const limit = parseInt(process.argv[4]);
// const tnxprivatekey = process.argv[5];
// const tnxpublickey = process.argv[6];
// const batchprivatekey = process.argv[7];
// const batchpublickey = process.argv[8];
// const apiURL = process.argv[9];

const tnxprivatekey ="10e796e4d43d51364abd0279975a889049e255961ad0f00b86840977f8273679";
const tnxpublickey = "032f2ecbb471f6f487b82c915f5bf26c6f0c7c5cc412b45d25ad232a943b11b9d4";
const batchprivatekey = "276fa81ae93014df52e8fdcc5912349aabfbcf60df3fb40dc1234500dd20bf3b";
const batchpublickey = "02d064de8ea6280c99cb909d31f18c37f371a1a29e37dc43ca96525bf874f9c879";
const apiURL = "10.1.0.222:8080";


var sig_array = fs.readFileSync('signatures.sig').toString().split("\n");
var results = [];

console.log("***** CONFIG *****")
console.log("nb_batch_parallele", nb_batch_parallele)
console.log("waiting_time", waiting_time)
console.log("limit", limit)
console.log("Load config in nodejs => ok")

function extractAllText(str) {
    const re = /"(.*?)"/g;
    const result = [];
    let current;
    while (current = re.exec(str)) {
        result.push(current.pop());
    }
    return result.length > 0
        ? result
        : [str];
}

function wait(milleseconds) {
    return new Promise(resolve => setTimeout(resolve, milleseconds))
}

async function send(sig_array, next) {
    var total = 0;
    var total_exit = 0;
    var total_success = 0;
    var total_error = 0;
    var i = 0;
    var p_list = {};
    for (sig of sig_array) {
        // console.log(sig)
        (function (i, total) {
            var cmd = `./transaction --mode cartp \
            --tnxprivatekey ${tnxprivatekey} \
            --tnxpublickey ${tnxpublickey} \
            --batchprivatekey ${batchprivatekey} \
            --batchpublickey ${batchpublickey} \
            --cmd crash \
            --accident_ID QmfM2r8seH2GiRaC4esTjeraXEachRt8ZsSeGaWTPLyMoG \
            --signature ${sig} \
            --dataPublicKey Bxm4djh5ap9zBb9YyYHzdw5j6v8IOaHn \
            --url http://${apiURL}/batches`;
            //console.log(cmd)
            var child = exec(cmd);
            //console.log(total, "start")

            // Add the child process to the list for tracking
            p_list[i] = { process: child, content: "" };

            // Listen for any response:
            child.stdout.on('data', function (data) {
                //console.log(child.pid, data);
                p_list[i].content += data;
                var tmp = extractAllText(data);
                if (tmp.length > 1 && data.indexOf("\"link\"") != -1) {
                    results.push(tmp[1])
                    if (verbose)
                        console.log(total, "=> OK");
                    total_success += 1;
                } else if (tmp.length > 1 && data.indexOf("\"link\"") == -1) {
                    if (verbose)
                        console.log(total, "=> Error");
                    total_error += 1;
                } else if (data.indexOf("Gateway") != -1) { //for 504 & 502 errors
                    if (verbose)
                        console.log(total, "=> Error");
                    total_error += 1;
                }
            });

            // Listen for any errors:
            // child.stderr.on('data', function (data) {
            //     console.log(child.pid, data);
            //     p_list[i].content += data;
            // });

            // Listen if the process closed
            child.on('close', function (exit_code) {
                total_exit += 1;
                //console.log(total_exit, "exit")
                if (exit_code != 0)
                    console.log('Closed before stop: Closing code: ', exit_code);
            });
        })(i, total)

        i += 1;
        total += 1;

        if (total >= limit) {
            //program should stop
            if (verbose)
                console.log("Waiting all process exit")
            while (total_exit < total) {
                await wait(500)
                process.stdout.write("\r .");
            }
            if (verbose)
                console.log("Finished nodejs")
            fs.writeFileSync("tmp.txt", results.join("\n"), { encoding: 'utf8', flag: 'w' })
            console.log("total_exit", total_exit)
            console.log("total_success", total_success)
            console.log("total_error", total_error)
            return next()
        }

        if (i == nb_batch_parallele) {
            if (verbose)
                console.log("Waiting", waiting_time, "ms")
            await wait(waiting_time)
            i = 0;
        }
    }
}


async.series([
    function (callback) {
        var cmd = `./transaction --mode cartp \
        --tnxprivatekey ${batchprivatekey} \
        --tnxpublickey ${batchpublickey} \
        --batchprivatekey 4540473db04512cdfb6decaa5cc14c2442d3d3c742b47bf19e0395c07aeb8d20 \
        --batchpublickey 02a47084f6228bf7eb91e1628140f5b717cad1d1166b4ad7665e88204e74f92e5c \
        --cmd new_car \
        --car_brand "Kittmobile" \
        --car_type "Danger" \
        --car_licence "X1-102-10V" \
        --url "http://${apiURL}/batches"`;
        var child = exec(cmd);

        // Listen for any response:
        child.stdout.on('data', function (data) {
            console.log(data);
        });
        // Listen if the process closed
        child.on('close', function (exit_code) {
            if (exit_code != 0)
                console.log('Closed before stop: Closing code: ', exit_code);
            callback();
        });
    },
    function (callback) {
        var cmd = `./transaction --mode cartp \
        --tnxprivatekey ${tnxprivatekey} \
        --tnxpublickey ${tnxpublickey} \
        --batchprivatekey ${batchprivatekey} \
        --batchpublickey ${batchpublickey} \
        --cmd new_owner \
        --owner_lastname "Pikachou" \
        --owner_name "Mr. V" \
        --owner_address "1 av Atlantis" \
        --owner_country "France" \
        --url "http://${apiURL}/batches"`;
        var child = exec(cmd);

        // Listen for any response:
        child.stdout.on('data', function (data) {
            console.log(data);
        });
        // Listen if the process closed
        child.on('close', function (exit_code) {
            if (exit_code != 0)
                console.log('Closed before stop: Closing code: ', exit_code);
            callback();
        });
    },
    function (callback) {
        console.log("Wait 5 sec for 1st stabilization...")
        setTimeout(callback, 5000);
    },
    function (callback) {
        send(sig_array, callback)
    },
    function(callback) {
        process.exit(0);
    }
])

