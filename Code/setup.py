from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from tomli import load
from json import load as jload
from web3 import Web3
import ipfs_api
from shutil import rmtree
from os import mkdir
import sys
from time import sleep
class SetUp:
    def __init__(self,):
        with open("config.toml","rb") as f:
            self.CONFIG = load(f)
        with open(self.CONFIG["BOOTSTRAP"]["CONTRACT_ABI"],"rb") as f:
            self.ABI = jload(f)
        self.CONN = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))
        self.CONTRACT = self.CONN.eth.contract(address=self.CONFIG["METADATA"]["CONTRACT_ADDRESS"],
                                          abi=self.ABI)

    def set_files(self):
        print("DO NOT FORGET TO RUN ipfs repo gc to clear IPFS")
        rmtree("keys",ignore_errors=True)
        print("Deleting Existing Keys")
        rmtree("runs",ignore_errors=True)
        print("Deleting Existing Runs")
        mkdir("runs")
        mkdir("keys")
        mkdir("./keys/manager")
        n = int(sys.argv[1])

        for x in range(0,n):
            mkdir("./keys/expert"+str(x)+"/")
 
        

    def key_generation(self,filepath,number):
        
        """
            Generate New Keys, save the private key and upload the publick key to IPFS
        """
        #Key Generation
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024, backend=default_backend())
        public_key = private_key.public_key()
        #Saving the Private Key in PEM file
        private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        with open(filepath+"private.pem", 'wb') as pem_out:
            pem_out.write(private_pem)
        with open(filepath+"public.pem", 'wb') as pem_out:
            pem_out.write(public_pem)
        hash = ipfs_api.http_client.add(filepath+"public.pem")
        hash = hash["Hash"]
        tra1 = self.CONTRACT.functions.updateExpertPublicKey(number,hash).transact()
        tx_receipt = self.CONN.eth.wait_for_transaction_receipt(tra1)
        print("Generated New Key and Updated the Smart Contract",hash)

s = SetUp()
s.set_files()
n = int(sys.argv[1])
s.key_generation("./keys/manager/",n)
for x in range(0,n):
    print(x)
    s.key_generation("./keys/expert"+str(x)+"/",x)
