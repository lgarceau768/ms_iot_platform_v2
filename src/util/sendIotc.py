import os, asyncio, sys, azure.iot.device, json, socket, const, datetime, subprocess
from azure.iot.device import X509
from azure.iot.device.aio import IoTHubDeviceClient
from getmac import get_mac_address
from util import rotatingLogger as logger

@asyncio.coroutine
async def connect():
    hostname = "iotc-edbc3300-b4bb-4461-8328-e2d8bf17d7a9.azure-devices.net"
    deviceID = socket.gethostname()

    cert = X509(
        cert_file = "/home/User1/certs/%s.pem" % deviceID,
        key_file = "/home/User1/certs/%s.key" % deviceID,
        pass_phrase = "1234" 
    )

    client = IoTHubDeviceClient.create_from_x509_certificate(
        hostname=hostname, device_id=deviceID, x509=cert,
    )
    await client.connect()
    logger.get_logger().info('Connected to IoT Central')
    return client

@asyncio.coroutine
async def sendMessages():
    # send init messages
    client = await connect()
    properties = ['hygieneStart, hygieneStop', 'hygieneLast', 'batteryLevel', 'serialNum']
    if client != None:
        # semd init messages
        await updateTwin()
        timestamp = '{"timestamp":"%s",' % datetime.datetime.now().isoformat()
        hardMac = '"hardwareMac":"%s",' % get_mac_address(interface='wlan0')
        netMac = '"networkMac":"%s",' % get_mac_address(interface='eth0')
        deviceID = '"deviceID":"%s",' % socket.gethostname()
        officeName = '"officeLocation":"%s",' % getProperty('officeName')
        roomName = '"roomName":"%s",' % getProperty('roomName')
        officeLocation = '"officeLocation":"%s"' % getProperty('officeLocation')
        command = ['hostname', '-I']
        output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        ip = '"ipAddress":"%s"}' % str(output)[2:].replace("\\n'",'')
        fullMsg = timestamp+hardMac+netMac+deviceID+officeName+ip
        await client.patch_twin_reported_properties(json.loads(fullMsg))
        await client.send_message('{"deviceEvent":"init"}')
        await client.disconnect()
        while True:
            removes = []
            client = None
            for i in range(len(const.MSG_TO_SEND)):
                if client == None:
                    client = await connect()

                lastTimeConnected = json.loads('{"lastTimeConnected":"%s"}' % datetime.datetime.now().isoformat())
                messageList = const.MSG_TO_SEND[i]
                jsonStr = '{'
                prop = False
                for k in range(len(messageList)):
                    if messageList[k][0] in properties:
                        prop = True
                    jsonStr = jsonStr+ '"%s":"%s",' % (messageList[k][0], messageList[k][1])
                jsonStr = jsonStr+'"deviceID":"%s"}' % socket.gethostname()
                jsonMsg = json.loads(jsonStr)
                if not prop:
                    logger.get_logger().info('Sending Telemetry:\n\t %s' % jsonMsg)
                    msg = azure.iot.device.Message(jsonMsg)
                    await client.send_message(msg)
                else:
                    
                    logger.get_logger().info('Sending Property:\n\t %s' % jsonMsg)
                    await client.patch_twin_reported_properties(jsonMsg)
                await client.patch_twin_reported_properties(lastTimeConnected)
                removes.append(messageList)
            for item in removes:
                const.MSG_TO_SEND.remove(item)
            if client != None:
                await client.disconnect()
                client = None
    else:
        logger.get_logger().error('Error in connecting to IoT Central')
    
@asyncio.coroutine
async def settingsChange():
    client = await connect()
    if client != None:
        while True:
            patch = await client.receive_twin_desired_properties_patch()
            if patch != None:
                await updateTwin()
    else:
        logger.get_logger().error('Error in IoT Client')
        #await connect()
    await client.disconnect()

@asyncio.coroutine 
async def updateTwin():
    client = await connect()
    if client != None:
        const.DEVICE_TWIN = await client.get_twin()
    else:
        logger.get_logger().error('Error Retreiving device twin with iot client')
        #await connect()
    await client.disconnect()
        
def getProperty(property):
    try:
        return const.DEVICE_TWIN['desired'][property]['value']
    except Exception as e:
        logger.get_logger().debug('Property %s not found' % property)
        return 'not_found'

@asyncio.coroutine
async def c2dCom():
    print('test') # waiting on kunal to show us how to do some of this stuff