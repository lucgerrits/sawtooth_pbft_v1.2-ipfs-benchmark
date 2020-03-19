

import socket
import sys
import json
import yaml
import requests

import logging

# from urllib.parse import urlencode
# import pycurl


# class MySocket:
#     """demonstration class only
#       - coded for clarity, not efficiency
#     """

#     def __init__(self, sock=None):
#         if sock is None:
#             self.sock = socket.socket(
#                             socket.AF_INET, socket.SOCK_STREAM)
#         else:
#             self.sock = sock

#     def connect(self, host, port):
#         self.sock.connect((host, port))

#     def mysend(self, msg):
#         totalsent = 0
#         while totalsent < MSGLEN:
#             sent = self.sock.send(msg[totalsent:])
#             if sent == 0:
#                 raise RuntimeError("socket connection broken")
#             totalsent = totalsent + sent

#     def myreceive(self):
#         chunks = []
#         bytes_recd = 0
#         while bytes_recd < MSGLEN:
#             chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
#             if chunk == b'':
#                 raise RuntimeError("socket connection broken")
#             chunks.append(chunk)
#             bytes_recd = bytes_recd + len(chunk)
#         return b''.join(chunks)

def myprint(mystring):
    sys.stdout.write(mystring + "\n")
    sys.stdout.flush()

# myprint('Start socket')
# # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     myprint("Dans le boucle")
#     sys.stdout.flush()
#     s.bind(('0.0.0.0', 81))
#     myprint("Bind ok")

#     s.listen(1)
#     myprint("after listen")

#     conn, addr = s.accept()
#     myprint("Accept")

#     with conn: 
#         myprint("Connected by {}".format(addr))
#         while True:
#             data = s.recv(1024)
#             myprint('Recieved : {}'.format(repr(data)))

# myprint("Exiting hello.py")

def transmitPubKeyAndSigToIPFSmodule(message):
    myprint(' #################################### My data is sent ####################################')
    publicKey = "Salut"
    myprint(" Raw Message : {}".format(message))

    # outputData = {}
    # dataform = str(message).strip("'<>() ").replace('\'', '\"')
    # outputData = json.loads(dataform.decode('utf-8'))
    # myprint("Data : {}".format(outputData))
    #outputData = json.loads(message)
    #print(outputData)
    #
    #myprint("Data to trasmit : {}".format(json.loads(message.decode('utf-8'))))
    #s=json.dumps({"PubKey" : publicKey, "Signature" : sig}, sort_keys=True).encode('utf-8')

    
    strMessage = message.decode("utf-8")
    res = yaml.load(strMessage)

    myprint(" Data dictionary : {}".format(res))


    ##############################################################################################
    myprint('******** Send Signature and data decryption key')
    #crl = pycurl.Curl()

    DataDecryptKey = res['PubKey']
    Signature = res['Signature']

    address = 'http://10.1.201:5000/sig_and_key/' + Signature + '/' + DataDecryptKey
    
    x = requests.post(address)
    myprint(" Data dictionary : {}".format(x.text))

    # crl.setopt(crl.URL, address)
    # crl.setopt(pycurl.POSTFIELDS, 1)
    # crl.perform()
    # crl.close()



myprint("In IPFS module")

HOST = '0.0.0.0'                 # Symbolic name meaning all available interfaces
PORT = 81 # Arbitrary non-privileged port
myprint(str(HOST))
myprint(str(PORT))
myprint("Listening...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

globaldata = b'empty'

while 1:

    conn, addr = s.accept()
    #myprint("conected by: {}".format(addr))

    while 1:
        try:
            data = conn.recv(1024)
            
            if not data: 
                break
            else: 
                if data == globaldata:
                    conn.sendall(b"ACK")
                    break
                else:
                    transmitPubKeyAndSigToIPFSmodule(data)
                    globaldata = data
                
            #myprint("FROM: {} ={}".format(addr, data))

            #if globaldata != data or i==0:
            #transmitPubKeyAndSigToIPFSmodule(data)
            #     globaldata = data    
            #     i=1   
            conn.sendall(b"ACK")
            
        except:
           print("Disconnected")
    
     
    conn.close()
    myprint("Closed")
    # if i == 1: #if data_last != data and data != 0:
    #     myprint("Data befor sending : {}".format(globaldata))
    #     transmitPubKeyAndSigToIPFSmodule(data)

myprint("Stop")
