import grpc
import partner_api2_pb2_grpc as api
from partner_api2_pb2 import *
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np

def data_api(cliente):
    partnerApiEndpoint = 'partner.emporiaenergy.com:50052'
    creds = grpc.ssl_channel_credentials()
    channel = grpc.secure_channel(partnerApiEndpoint, creds)
    stub = api.PartnerApiStub(channel)
    request = AuthenticationRequest()
    request.partner_email = 'hsoto@cigepty.com'
    request.password = 'hsm280466'
    auth_response = stub.Authenticate(request=request)
    auth_token = auth_response.auth_token
    inventoryRequest = DeviceInventoryRequest()
    inventoryRequest.auth_token = auth_token
    inventoryResponse = stub.GetDevices(inventoryRequest)
    deviceUsageRequest = DeviceUsageRequest()
    deviceUsageRequest.auth_token = auth_token
    date_range = pd.date_range(start=datetime.now()-relativedelta(days=90), end=datetime.now()-relativedelta(days=1))
    now = int((datetime.now().replace(microsecond=0) + timedelta(seconds=1)).timestamp())
    deviceUsageRequest.start_epoch_seconds = now - len(date_range) * 24 * 60 * 60 # one hour of seconds
    deviceUsageRequest.end_epoch_seconds = now
    deviceUsageRequest.scale = DataResolution.Days
    deviceUsageRequest.channels = DeviceUsageRequest.UsageChannel.ALL
    usageResponse = stub.GetUsageData(deviceUsageRequest)

    names = {}; data = pd.DataFrame()
    for device in inventoryResponse.devices: 
        if cliente.lower() in device.device_name.lower():
            device_name = device.device_name
            device_id = device.manufacturer_device_id
            for circuit in device.circuit_infos:
                if circuit.name != '': 
                    names[circuit.channel_number] = circuit.sub_type+'-'+circuit.name
    device_found =  [i for i in usageResponse.device_usages if i.manufacturer_device_id==device_id][0]
    days = len(device_found.channel_usages[0].usages)
    data['Time Bucket'] = pd.date_range(start=datetime.now()-relativedelta(days=days)+relativedelta(days=1),end=datetime.now()).date
    for circuit in device_found.channel_usages:
        if circuit.channel in names.keys():
            data[f'{circuit.channel}-{names[circuit.channel]}'] = np.array(circuit.usages)/1000
        if circuit.channel == 1: data[f'{circuit.channel}-Mains_A'] = np.array(circuit.usages)/1000
        if circuit.channel == 2: data[f'{circuit.channel}-Mains_B'] = np.array(circuit.usages)/1000
        if circuit.channel == 3: data[f'{circuit.channel}-Mains_C'] = np.array(circuit.usages)/1000
    
    return device_name, data
