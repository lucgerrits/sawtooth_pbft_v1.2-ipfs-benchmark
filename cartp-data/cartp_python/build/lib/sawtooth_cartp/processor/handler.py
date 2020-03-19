# Copyright 2016 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
import traceback
# traceback.print_stack()
import logging
import hashlib

import cbor
import json
import socket
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError


LOGGER = logging.getLogger(__name__)


VALID_TNX_CMDS = 'new_car', 'new_owner', 'crash'

CAR_ID_LENGTH = 66
MAX_OWNER_LENGTH = 32

FAMILY_NAME = 'cartp'

CARTP_ADDRESS_PREFIX = hashlib.sha512(
    FAMILY_NAME.encode('utf-8')).hexdigest()[0:6]


def make_cartp_address(car_id, data_type):
    if data_type in ["car", "owner", "crash"]:
        return CARTP_ADDRESS_PREFIX \
            + hashlib.sha512(data_type.encode('utf-8')).hexdigest()[:4] \
            + hashlib.sha512(car_id.encode('utf-8')).hexdigest()[:60]
    elif data_type == "factory_settings":
        return "000000a87cb5eafdcca6a89a6f6aa92a4b7cb206c8aaa93d80a76817373ca1c7634a4b"
    else:
        LOGGER.debug("Trying to access strange address, skiping...")
        return None

# def make_settings_cartp_factory_address():
#     return "000000a87cb5eafdcca6a89a6f6aa92a4b7cb206c8aaa93d80a76817373ca1c7634a4b"
#     # return '000000' + hashlib.sha256('sawtooth'.encode()).hexdigest()[:16] \
#     #     + hashlib.sha256('cartp'.encode()).hexdigest()[:16] \
#     #         + hashlib.sha256('factory'.encode()).hexdigest()[:16] \
#     #             + hashlib.sha256('members'.encode()).hexdigest()[:16]


class cartpTransactionHandler(TransactionHandler):
    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [CARTP_ADDRESS_PREFIX]

    def apply(self, transaction, context):

        tnx_cmd, options = _unpack_transaction(transaction)
        states = {}
        # for adding a new car we need to access factory members public keys:
        # (only in read mode: no SET state)
        if tnx_cmd == "new_car":
            states["factory_settings"] = _get_state_data(
                "", "factory_settings", context)
            states["car"] = _get_state_data(options["car_id"], "car", context)

        elif tnx_cmd == "new_owner":
            states["car"] = _get_state_data(options["car_id"], "car", context)
            states["owner"] = _get_state_data(
                options["car_id"], "owner", context)

        elif tnx_cmd == "crash":
            states["car"] = _get_state_data(options["car_id"], "car", context)
            states["owner"] = _get_state_data(
                options["car_id"], "owner", context)
            states["crash_owner"] = _get_state_data(
                options["owner_id"], "crash", context)
            states["crash_car"] = _get_state_data(
                options["car_id"], "crash", context)

        updated_states = _do_cartp(tnx_cmd, options, states, transaction)

        # SET states:
        if tnx_cmd == "new_car":
            _set_state_data(options["car_id"], "car",
                            updated_states["car"], context)
        elif tnx_cmd == "new_owner":
            _set_state_data(options["car_id"], "owner",
                            updated_states["owner"], context)
        elif tnx_cmd == "crash":
            _set_state_data(options["owner_id"], "crash",
                            updated_states["crash_owner"], context)
            _set_state_data(options["car_id"], "crash",
                            updated_states["crash_car"], context)

       
def _unpack_transaction(transaction):
    tnx_cmd, options = _decode_transaction(transaction)
    _validate_car_id(options["car_id"])
    return tnx_cmd, options


def _decode_transaction(transaction):
    options = {
        "new_car": {
            "factory_id": None,
            "car_id": None,
            "car_brand": None,
            "car_type": None,
            "car_licence": None
        },
        "new_owner": {
            "car_id": None,
            "owner_id": None,
            "owner_lastname": None,
            "owner_name": None,
            "owner_address": None,
            "owner_country": None,
            #"owner_contact": None,
            # "owner_picture": None,
            # "owner_picture_ext": None
        },
        "crash": {
            "car_id": None,
            "owner_id": None,
            "accident_ID": None, # IPFS address (Hash of the car data)
            "signature": None, # Signatrure of IoT device
            "dataPublicKey": None, # Data encryption Public Key 
            # "date_of_the_accident": None,
            # "accident_ID": None,
            
            # "hour": None,
            # "location_country": None,
            # "location_place": None,

            # "odometer": None,
            # "radar_front": None,
            # "radar_back": None,
            # "radar_right": None,
            # "radar_left": None,
            # "collision_front": None,
            # "collision_back": None,
            # "collision_right": None,
            # "collision_left": None,

            # "picture_front": None,
            # "picture_front_ext": None,
            # "picture_back": None,
            # "picture_back_ext": None,
            # "picture_right": None,
            # "picture_right_ext": None,
            # "picture_left": None,
            # "picture_left_ext": None

            # "injured_even_slightly": None,_get_state_dataar": None,P
            # "witnesses_contact": None,

            # "driver_id": None,

            # "driver_lastname": None,
            # "driver_name": None,
            # "driver_address": None,
            # "driver_country": None,
            # "driver_zip_code": None,
            # "driver_contact": None,

            # "car_brand": None,
            # "car_type": None,
            # "car_licence": None,

            # "shock_point_initial_to_vehicle": None,
        }
    }
    try:
        content = cbor.loads(transaction.payload)
    except:
        raise InvalidTransaction('Invalid payload serialization')

    try:
        tnx_cmd = content['tnx_cmd']
    except AttributeError:
        raise InvalidTransaction('tnx_cmd is required')

    if tnx_cmd not in VALID_TNX_CMDS:
        raise InvalidTransaction(
            'tnx_cmd must be {}'.format(",".join(VALID_TNX_CMDS)))
    else:
        for key in options[tnx_cmd]:
            try:
                options[tnx_cmd][key] = content[key]
            except AttributeError:
                raise InvalidTransaction('{} is required'.format(key))

    return tnx_cmd, options[tnx_cmd]


def _validate_car_id(car_id):
    if not isinstance(car_id, str) \
        or len(car_id) != CAR_ID_LENGTH \
            or len(car_id) == 0:
        raise InvalidTransaction(
            'car_id must be a string of exactly {} characters'.format(
                CAR_ID_LENGTH))


def _get_state_data(car_id, data_type, context):
    if data_type == "factory_settings":
        address = make_cartp_address(car_id, data_type)

        state_entries = context.get_state([address])
        try:
            return "".join(map(chr, state_entries[0].data))
        except IndexError:
            return {}
        except:
            raise InternalError('Failed to load state data (settings)')
    else:
        address = make_cartp_address(car_id, data_type)

        state_entries = context.get_state([address])
        try:
            return cbor.loads(state_entries[0].data)
        except IndexError:
            return {}
        except:
            raise InternalError('Failed to load state data (cartp)')


def _set_state_data(car_id, data_type, state, context):
    address = make_cartp_address(car_id, data_type)

    encoded = cbor.dumps(state)

    addresses = context.set_state({address: encoded})

    if not addresses:
        raise InternalError('State error')


def _do_cartp(tnx_cmd, options, states, transaction):
    tnx_cmds = {
        'new_car': _do_new_car,
        'new_owner': _do_new_owner,
        'crash': _do_crash
    }

    try:
        return tnx_cmds[tnx_cmd](options, states, transaction)
    except KeyError:
        # This would be a programming error.
        raise InternalError('Unhandled tnx_cmd: {}'.format(tnx_cmd))


def _do_new_car(options, states, transaction):
    msg = 'Setting new car with car_id:"{n}"'.format(n=options["car_id"])
    LOGGER.debug(msg)

    # if factory exist
    if options["factory_id"] not in states["factory_settings"]:
        raise InvalidTransaction(
            'ERROR: Factory doesn\'t exists: factory_id: {}'.format(options["factory_id"]))

    # if car exist
    if "data" in states["car"]:
        if "car_id" in states["car"]["data"]:
            if options["car_id"] == states["car"]["data"]["car_id"]:
                raise InvalidTransaction(
                    'ERROR: Already exists: car_id: {}'.format(options["car_id"]))

    updated = states
    updated["car"] = {k: v for k, v in states["car"].items()}
    updated["car"]["data"] = {
        "factory_id": options["factory_id"],
        "car_id": options["car_id"],
        "car_brand": options["car_brand"],
        "car_type": options["car_type"],
        "car_licence": options["car_licence"]
    }

    return updated


def _do_new_owner(options, states, transaction):
    msg = 'Setting new owner of car_id:"{n}" to owner_id:{v}'.format(
        n=options["car_id"], v=options["owner_id"])
    LOGGER.debug(msg)

    # if car exist
    test = False
    if "data" in states["car"]:
        if "car_id" in states["car"]["data"]:
            if options["car_id"] == states["car"]["data"]["car_id"]:
                # LOGGER.debug("Car exist, adding owner...")
                bob=0
            else:
                test = True
        else:
            test = True
    else:
        test = True
    if test:
        raise InvalidTransaction(
            'ERROR: Car not exists: car_id: {}'.format(options["car_id"]))

    # if already owner
    if "data" in states["owner"]:
        if "owner_id" in states["owner"]["data"]:
            if options["owner_id"] == states["owner"]["data"]["owner_id"]:
                raise InvalidTransaction(
                    'ERROR: Already owner of car_id: {}'.format(options["car_id"]))

    updated = states
    updated["owner"] = {k: v for k, v in states["owner"].items()}
    updated["owner"]["data"] = {
        "car_id": options["car_id"],
        "owner_id": options["owner_id"],
        "owner_lastname": options["owner_lastname"],
        "owner_name": options["owner_name"],
        "owner_address": options["owner_address"],
        "owner_country": options["owner_country"],
        #"owner_contact": options["owner_contact"],
        #"owner_picture": options["owner_picture"],
        #"owner_picture_ext": options["owner_picture_ext"]
    }

    return updated


def _do_crash(options, states, transaction):
    msg = 'Setting crash of car_id:"{n}" to owner_id:{v}'.format(
        n=options["car_id"], v=options["owner_id"])
    LOGGER.debug(msg)
    #LOGGER.debug(transaction.signature)

    # if car exist
    test = False
    if "data" in states["car"]:
        if "car_id" in states["car"]["data"]:
            if options["car_id"] == states["car"]["data"]["car_id"]:
                #LOGGER.debug("Car exist, adding crash...")
                bob=0
            else:
                test = True
        else:
            test = True
    else:
        test = True
    if test:
        raise InvalidTransaction(
            'ERROR: Car not exists: car_id: {}'.format(options["car_id"]))

    updated = states
    updated["crash_car"] = {k: v for k, v in states["crash_car"].items()}
    if "data" in states["crash_car"]:
        updated["crash_car"]["data"].append(transaction.signature)
    else:
        updated["crash_car"]["data"] = [transaction.signature]

    updated["crash_owner"] = {k: v for k, v in states["crash_owner"].items()}
    if "data" in states["crash_owner"]:
        updated["crash_owner"]["data"].append(transaction.signature)
    else:
        updated["crash_owner"]["data"] = [transaction.signature]

    return updated

class MySocket:
    """demonstration class only
      - coded for clarity, not efficiency
    """

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg):
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def myreceive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return b''.join(chunks)