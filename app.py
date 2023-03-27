import shelve
import requests
from flask import Flask, render_template, request
from flask_restful import Resource, Api, reqparse


APP = Flask(__name__)
API = Api(APP)

# API
class Devices(Resource):
    def get(self):
        db = shelve.open('devices')
        devices = []
        for identifier in db:
            devices.append(db[identifier])
        db.close()
        return {'devices': devices}, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('identifier', required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('device_type', required=True)
        parser.add_argument('controller_gateway', required=True)
        parser.add_argument('icon', required=True)
        parser.add_argument('controller_port')
        parser.add_argument('hue_user')
        args = parser.parse_args()
        db = shelve.open('devices')
        db[args['identifier']] = args
        db.close()
        return {'message': 'Device registered', 'data': args}, 201

class Device(Resource):
    def get(self, identifier):
        db = shelve.open('devices')
        device = db[identifier]
        db.close()
        return {'data': device}, 200

    def delete(self, identifier):
        db = shelve.open('devices')
        if not (identifier in db):
            return {'message': 'Device not found', 'data': {}}, 404
        del db[identifier]
        db.close()
        return '', 204

API.add_resource(Devices, '/devices')
API.add_resource(Device, '/device/<string:identifier>')

# Web app
@APP.route('/')
def index():    
    db = shelve.open('devices')
    devices = []
    for identifier in db:
        devices.append(db[identifier])
    db.close()
    return render_template('index.html', devices=devices), 200

@APP.route('/device/<string:identifier>/flip-state')
def flip_state(identifier):
    device_metadata = requests.get(f'http://{request.host}/device/{identifier}').json()
    device_ip = device_metadata['data']['controller_gateway']
    device_port = device_metadata['data']['controller_port']
    device_state = requests.post(
        url=f'http://{device_ip}:{device_port}/zeroconf/info',
        json={ "data": {} }
    ).json()
    if device_state['data']['switch'] == 'off':
        new_state = 'on'
    elif device_state['data']['switch'] == 'on':
        new_state = 'off'    
    requests.post(
        url=f'http://{device_ip}:{device_port}/zeroconf/switch',
        json={ 'data': {'switch': new_state} }
    )
    get_new_state = requests.post(
        url=f'http://{device_ip}:{device_port}/zeroconf/info',
        json={ "data": {} }
    ).json()['data']
    return get_new_state

@APP.route('/device/<string:identifier>/get-state')
def get_state(identifier):
    device_metadata = requests.get(f'http://{request.host}/device/{identifier}')
    device_ip = device_metadata.json()['data']['controller_gateway']
    device_port = device_metadata.json()['data']['controller_port']
    device_state = requests.post(
        url=f'http://{device_ip}:{device_port}/zeroconf/info',
        json={ "data": {} }
    ).json()
    if device_state['data']['switch'] == 'off':
        return {'state': 'off'}, 200
    elif device_state['data']['switch'] == 'on':
        return {'state': 'on'}, 200
