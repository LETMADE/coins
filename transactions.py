import db
import hashlib
import os
import bitcoin
import json
import requests
import coinprism
import util

default_fee = 1000

def queue_issuing_tx(source_address, recipient_address, source_private, metadata, amount, name, identifier):
    if metadata[0:2]== "u=":
        metadata = "u="+util.shorten_url(metadata[2:len(metadata)])
    dbstring = "insert into color_issue_tx_queue values ('"+str(source_address)+"', '"+str(source_private)+"', '"+str(recipient_address)+"', "+str(default_fee)+", '', "+str(amount)+", False, '', '"+str(metadata)+"', '"+str(identifier)+"', '"+str(name)+"');"
    db.dbexecute(dbstring, False)

def queue_transfer_tx(sender_public, sender_private, recipient_public, amount, metadata, asset_address, identifier):
    dbstring = "insert into color_transfer_tx_queue values ('"+str(sender_public)+"', '"+str(sender_private)+"', '"+str(recipient_public)+"', "+str(default_fee)+", '"+str(asset_address)+"', "+str(amount)+", False, '','"+str(metadata)+"', '"+str(identifier)+"');"
    db.dbexecute(dbstring, False)

def random_id():
    return str(hashlib.sha256(str(os.urandom(100))).hexdigest())

def queue_btc_tx(sender_public, sender_private, recipient_public, amount, identifier):
    print sender_public
    print sender_private
    print recipient_public
    print amount
    amount = float(amount) * 100000000
    dbstring = "insert into btc_tx_queue values ('"+str(sender_public)+"', '"+str(sender_private)+"', '"+str(recipient_public)+"', "+str(default_fee)+", "+str(amount)+", False,'', '"+str(identifier)+"');"
    db.dbexecute(dbstring, False)

def send_btc_chain(from_addr, destination_address, btc_value):
    btc_value = btc_value * 100000000
    data = {}
    data['inputs'] = [{'address': from_addr}]
    data['outputs'] = [{'address': destination_address, 'amount': btc_value}]
    data['miner_fee_rate'] = default_fee
    d = json.dumps(data)
    print d
    authstuff=(os.environ['CHAIN_API_KEY'], os.environ['CHAIN_API_KEY_SECRET'] )
    url = "https://api.chain.com/v2/bitcoin/transactions/build"
    r = requests.post(url, data=d, auth=authstuff)
    return str(json.loads(r.content)['unsigned_hex'])

def send_btc(from_addr, private_key, destination_address, btc_value):
    a = send_btc_chain(from_addr, destination_address, btc_value)
    b = coinprism.sign_tx(a, private_key)
    return coinprism.pushtx(b)
