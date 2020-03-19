from flask import Flask
from flask import request
import secp256k1
import binascii
import os
import sys
import ipfshttpclient
import time

app = Flask(__name__)

# curl -X POST http://localhost:5000/sig_and_key/<Sig>/<Key>
@app.route('/sig_and_key/<Sig>/<Key>', methods=['GET', 'POST'])
def ListenSocket(Sig,Key):
	if request.method == 'POST':
		return 'Signature and Data Decryption Key are received'
	else:
		return 'NOT A POST REQUEST\n'



if __name__ == "__main__":
	app.run(host='0.0.0.0')
	