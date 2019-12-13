import os, sys, asyncio, const as const, configparser, time, datetime, socket
from util import hygieneData
from util import rotatingLogger as logger, hygieneData, readOld
# config
config = configparser.ConfigParser()
config.read(const.CONFIG_PATH)



@asyncio.coroutine
async def interpret():
    compTimer = time.time()/60
    # deviceStatus
    deviceState = 'idle'

    # runTime
    runTimeLast = compTimer
    runTimeDelta = abs(runTimeLast-compTimer)
    runTimeInt = float(config.get('Time', 'runTime'))

    # use/idle time
    timeMsgLast = compTimer
    timeInt = float(config.get('Time', 'time'))
    timeMsgDelta = abs(timeMsgLast-compTimer)
    changeTime = compTimer
    changeTimeDelta = abs(changeTime-compTimer)

    # hygieneTime
    hygieneTimeLast = compTimer
    hygieneTimeDelta = abs(hygieneTimeLast-compTimer)
    hygieneTimeInt = float(config.get('Time', 'hygieneTime'))
    hygieneInProgress = False    
    old8 = '00 00 00 00 00 00 00'
    old10 = '00 00 00 00 00 00 00'

    # batteryLevel
    batteryLast = 0
    

    ##print('running')
    while True:
        # messages to remove after loop
        remove = []
        ##print('looping')
        compTimer = time.time()/60
        timestamp = datetime.datetime.now().isoformat()
        timestamp = ['timestamp', str(timestamp)]
        
        # need to interpret the can data
        for data in const.CAN_DATA:
            #data[1] = data[1].strip().replace(' ','')
            compTimer = time.time()/60
            already = False
            already2 = False
            messages = []
            if len(data) != 3:
                remove.append(data)
            # need to see if this is a new/old message
            else:
                remove.append(data)
                # runtime
                runTimeDelta = abs(runTimeLast-compTimer)
                ##print('rtime: '+str(runTimeDelta))
                if runTimeDelta >= runTimeInt:
                    messages.append([['runTime', str(runTimeInt/60.0)]])
                    messages.append([timestamp, ['timeType', 'runTime'], ['timeAmt', str(runTimeInt/60.0)]])
                    runTimeLast = compTimer
                
                # hygiene
                hygieneTimeDelta = abs(hygieneTimeLast-compTimer)
                if hygieneTimeDelta >= hygieneTimeInt:
                    # need to read the old data
                    hygData = hygieneData.getHygieneInfo()
                    if 'no_mem' in hygData:
                        messages.append([timestamp, ['hygieneLast','-1'], ['hygieneType','no_mem'], ['hygieneStart','no_mem'], ['hygieneStop','no_mem']])
                    else:
                        start = hygData[0]
                        stop = hygData[1]
                        
                        typeHyg = hygData[2]
                        # need to find difference in hours btw now and the last one
                        now = datetime.datetime.now()
                        then = datetime.datetime.strptime(str(stop), '%Y-%m-%dT%H:%M:%S.%f')
                        diff = now-then
                        hours = (float(diff.seconds)/60.0/60.0) + int(diff.days) * 24
                        hours = ['hygieneLast', str(hours)]
                        messages.append([timestamp, hours, ['hygieneType', typeHyg], ['hygieneStart', start], ['hygieneStop', stop]])
                    hygieneTimeLast = compTimer
                
                # now use and idleTime
                whichTime = alreadyHave(data)
                idle = True
                use = False
                newMsg = False

                if whichTime == use:
                    logger.get_logger().info('test')
                    const.MSG_TO_RECORD.append(data)
                    if (data[1] == '0x08') and (old8 != (" ".join(data[2].split()[0:1])+' '+" ".join(data[2].split()[2:9]))):
                        old8 = " ".join(data[2].split()[0:1])+' '+" ".join(data[2].split()[2:9])
                        changeTime = compTimer
                        # new canMsg
                        newMsg = True
                    elif (data[1] == '0x10') and (old10 != (" ".join(data[2].split()[0:3])+' '+" ".join(data[2].split()[4:9]))):
                        old10 = " ".join(data[2].split()[0:3])+' '+" ".join(data[2].split()[4:9])
                        changeTime = compTimer
                        # new canMsg
                        newMsg = True
                    elif (data[1] != '0x08') and (data[1] != '0x10'):
                        changeTime = compTimer
                        # new canMsg
                        newMsg = True


                    
                #logger.get_logger().info('===========Before Calc')
                timeMsgDelta = abs(timeMsgLast-compTimer)
                if timeMsgDelta >= timeInt:
                    changeTimeDelta = abs(changeTime-compTimer)
                    if changeTimeDelta >= timeInt:
                        messages.append([['idleTime', str(timeInt/60.0)]])
                        messages.append([timestamp, ['timeType', 'idleTime'], ['timeAmt', str(timeInt/60.0)]])
                    else:
                        messages.append([['useTime', str(timeInt/60.0)]])
                        messages.append([timestamp, ['timeType', 'useTime'], ['timeAmt', str(timeInt/60.0)]])
                    timeMsgLast = compTimer

                #logger.get_logger().info('===========After Calc')
                if newMsg:
                    
                    logger.get_logger().info('useCode: '+str(data))
                    #logger.get_logger().info('msgToRecord: '+str(const.MSG_TO_RECORD))
                    const.MSG_TO_RECORD.append(data)
                   
                    ### check for other codes as well
                    canID = data[1]
                    message = data[2].split(' ')
                    #logger.get_logger().info(canID)
                    # errorMessage
                    if canID == '0x402':
                        #logger.get_logger().info(str(message[2]))
                        errorMessage = getErrorMessage(data[2])
                        #logger.get_logger().info(str(errorMessage))
                        if errorMessage[1] is True:
                            messages.append([['errorMessage', str(errorMessage[0])], ['controlByte', message[0]], timestamp])

                    # hygiene status
                    if canID == '0x08':
                        if message[5] != '80':      
                            # test without the hygiene in progress variable being used
                            #hygieneInProgress = True                      
                            if message[4] == '88' and message[5] == '01' and not hygieneInProgress:
                                now = datetime.datetime.now().isoformat()
                                hygieneInProgress = True
                                hygType = ['hygieneType', 'in_progress']
                                hygStart = ['hygieneStart', now]
                                hygStop = ['hygieneStop', '']
                                # test
                                hygieneData.setHygieneInfo(now, 'no_mem', 'no_mem')
                                hygLast = ['hygieneLast','0']
                                if not already:
                                    messages.append([timestamp, hygLast, hygType, hygStart, hygStop])
                                    messages.append([['hygieneEvent', 'started']])
                                    already = True
                            if message[5] == '00' and hygieneInProgress and (message[4] == '09' or message[4] == '01'):
                                now = datetime.datetime.now().isoformat()
                                hygieneType = ''
                                if message[4] == '01':
                                    hygieneType = 'germ_reduction'
                                elif message[4] == '09':
                                    hygieneType = 'intensive_germ_reduction'
                                hygieneInProgress = False
                                hygLast = ['hygieneLast', '0']
                                hygType = ['hygieneType', hygieneType]
                                hygStop = ['hygieneStop', now]
                                oldData = hygieneData.getHygieneInfo()
                                oldStart = oldData[0]
                                hygStart = ['hygieneStart', oldStart]
                                hygieneData.setHygieneInfo(oldStart, now, hygieneType)
                                if not already2:
                                    messages.append([timestamp, hygLast, hygType, hygStart, hygStop])
                                    messages.append([['hygieneEvent', 'started']])
                                    already2 = True
                                messages.append([timestamp, hygLast, hygType, hygStart, hygStop])
                                messages.append([['hygieneEvent', '%s_completed' % hygieneType]])
                    
                    # battery level
                    if canID == '0x08':
                        # need to see if it was already sent
                        if abs(batteryLast-compTimer) > 0.5:
                            bt = message[7]
                            msg = ['batteryLevel', '']
                            if bt == '00':
                                msg[1] = 'n/a'
                            elif bt == '01':
                                msg[1] = 'charged'
                            elif bt == '02':
                                msg[1] = 'low'
                            elif bt == '03':
                                msg[1] = 'very_low'
                            elif bt == '04':
                                msg[1] = 'empty'
                            else:
                                break
                            already = False
                            msg = [['batteryLevel', msg[1]], ['deviceID', socket.gethostname()], ['timestamp', datetime.datetime.now().isoformat()]]
                            for msg in const.MSG_TO_SEND:                            
                                for item in msg:
                                    if 'battery' in item[0][0]:
                                        already = True
                            if not already:
                                messages.append(msg)
                            batteryLast = compTimer

                    # serial number
                    if canID == '0x419' and message[0] == '06':
                        # update serial number
                        hexNum = str(message[3])+str(message[4])+str(message[5])+str(message[6])
                        srlNo = str(int(hexNum, 16))
                        updateSerialNo(srlNo)
             
            if len(messages) > 0:
                logger.get_logger().info('data: %s' % str(messages))
                for msg in messages:
                    const.MSG_TO_SEND.append(msg)

        for item in remove:
            const.CAN_DATA.remove(item)
                
                             

# alreadyHave function - will return true of the message is already seen, retuyrn false if the message is new
# idle - true
# use - false
def alreadyHave(data):
    #time.sleep(1)
    idle = True
    use = False
    returnType = None
    oldCode = None
    found = False
    for item in const.CAN_CODES:
        if item[1].strip().replace(' ','') == data[1].strip().replace(' ',''):
            found = True
            oldCode = item
            # same can code
            if item[2].strip().replace(' ','').lower() == data[2].strip().replace(' ','').lower():
                # the same can message
                item = data
                returnType = idle
            else:
                # new can message                
                #print('list:\n'+str(const.CAN_CODES))
                #print('useHere: '+str(data))
                returnType = use
    if oldCode != None:
        #print('removing old code')
        const.CAN_CODES.remove(oldCode)
        const.CAN_CODES.append(data)
        
        return returnType
    if not found:
        const.CAN_CODES.append(data)
        return use

# pull the error messsage from the code:
def getErrorMessage(canMessage):
    mgsArray = canMessage.split(' ')
    hexID = mgsArray[2]
    ##print('hexID: '+str(hexID))
    hexID = hexID.upper()
    errorCodes = {
        '20' : 'ID 32: Heartbeat Gateway missing',
        '21' : 'ID 33: CAN node missing',
        '22' : 'ID 34: Gateway EEPROM error',
        '23' : 'ID 35: CAN error (warning / busoff)',
        '24' : 'ID 36: CAN error (warning / busoff)',
        '25' : 'ID 37: CAN error (warning / busoff)',
        '26' : 'ID 38: CAN error (warning / busoff)',
        '30' : 'ID 48: Chair learning A1 POT',
        '31' : 'ID 49: Chair learning A2 POT',
        '32' : 'ID 50: Chair A1 Acknowledge',
        '33' : 'ID 51: Chair A2 Acknowledge',
        '34' : 'ID 52: I2C water block ACK error',
        '35' : 'ID 53: Assistant element ACK',
        '36' : 'ID 54: Foot control Acknowledge',
        '37' : 'ID 55: Chair A3 Acknowledge',
        '38' : 'ID 56: Please charge foot control',
        '39' : 'ID 57: Chair learning required',
        '3A' : 'ID 58: Unit: Timeout IIC internal',
        '3B' : 'ID 59: Unit: Timeout IIC external',
        '3F' : 'ID 63: Reset Unit IIC external',
        '40' : 'ID 64: Message Leakage water',
        '41' : 'ID 65: Safety shut-off Bowl',
        '42' : 'ID 66:Amalgam separator erro',
        '43' : 'ID 67: Oxygenal empty',
        '44' : 'ID 68: Please perform service',
        '45' : 'ID 69: Intensive germ reduction',
        '46' : 'ID 70: DEKA. Bottle is empty',
        '47' : 'ID 71: No Oxygenal bottle',
        '48' : 'ID 72: DEKA. No bottle',
        '49' : 'ID 73: Low Oxygenal level',
        '4A' : 'ID 74: CENTRAmat empty',
        '4B' : 'ID 75: CENTRAmat too full',
        '4C' : 'ID 76: Unit DC 24 exceeded',
        '4D' : 'ID 77: More than 20% less',
        '50' : 'ID 80: Safety shut-off for chair',
        '51' : 'ID 81: Safety shutoff for the',
        '53' : 'ID 83: Safety shut-off on assistant',
        '54' : 'ID 84: Safety shut-off for spittoon',
        '55' : 'ID 85: Safety shut-off of stirrup',
        '60' : 'ID 96: Chair E30 - Chair learning',
        '61' : 'ID 97: Chair E30 - Motor',
        '62' : 'ID 98: Chair E 30 - Motor',
        '63' : 'ID 99: Chair E30 - Motor',
        '64' : 'ID 100: Chair E30 - EEPROM error',
        '65' : 'ID 101: Chair E30 - Undervoltage/',
        '68' : 'ID 104: Chair E30 - Vacustopp',
        '69' : 'ID 105: Chair E30 - Safety shut-off kick plate',
        '6A' : 'ID 106: Chair E30 - Safety shut-off backrest',
        '6B' : 'ID 107: Chair E30 - Safety shut-off seat',
        '6C' : 'ID 108: Chair E30 - Safety shut-off foot rest',
        '80' : 'ID 128: Reg. Data Contr. of unit',
        '81' : 'ID 129: Reg. Data Contr. Dentist',
        '82' : 'ID 130: Reg. data IMS missing',
        '83' : 'ID 131: Reg. data of LED light',
        '84' : 'ID 132: Reg. Data Contr. Unit',
        '85' : 'ID 133: Heartbeat Contr. Unit',
        '86' : 'ID 134: Heartbeat Contr. Dentist',
        '87' : 'ID 135: Heartbeat LED light',
        '8C' : 'ID 140: Error during SD card',
        '8D' : 'ID 141: Error during EEPROM',
        '8E' : 'ID 142: Error during Ethernet',
        '8F' : 'ID 143: Error during Gateway',
        '90' : 'ID 144: Error during unit software',
        '91' : 'ID 145: Error during dentist',
        '92' : 'ID 146: Error during IMS software',
        '93' : 'ID 147: Error in ERGOcom communication',
        '94' : 'ID 148: Error init config.',
        '95' : 'ID 149: Error init error memory',
        '96' : 'ID 150: Firmware Update Set is',
        '97' : 'ID 151: Invalid firmware combination',
        '98' : 'ID 152: Operation in DEBUG',
        '9B' : 'ID 155: Ethernet link lost',
        '9C' : 'ID 156: Error access update',
        '9D' : 'ID 157: Unexpected Reset',
        '9E' : 'ID 158: Unexpected Reset',
        '9F' : 'ID 159: Gateway CAN BusWarn',
        'A0' : 'ID 160: Gateway CAN BusOff',
        'A1' : 'ID 161: Invalid CMS configuration',
        'A2' : 'ID 162: Lost connection to CMS',
        'A3' : 'ID 163: No response from CMS',
        'A4' : 'ID 164: Faulty CMS server',
        'A5' : 'ID 165: CMS server login failed',
        'A6' : 'ID 166: Reg. Data Contr. Dentist',
        'A7' : 'ID 167: Reg. data of LED light',
        'A8' : 'ID 168: Error in FW update of',
        'A9' : 'ID 169: LED light generic error',
        '100' : 'ID 256: Invalid error number',
        '101' : 'ID 257: Timeout CAN',
        '102' : 'ID 258: Timeout CAN STARTER',
        '103' : 'ID 259: CAN IMS TX buffer',
        '104' : 'ID 260: menu_autochange: unknown',
        '105' : 'ID 261: Water block pressure',
        '106' : 'ID 262: Timeout CAN',
        '107' : 'ID 263: EEPROM error',
        '108' : 'ID 264: Operation in DEBUG',
        '109' : 'ID 265: Dentist control do not',
        '10A' : 'ID 266: Heartbeat Gateway',
        '10B' : 'ID 267: Stepper motor electr.',
        '10C' : 'ID 268: Stepper motor temperature',
        '10D' : 'ID 269: Timeout stepper motor',
        '10E' : 'ID 270: Dentist control unit key',
        '1C0' : 'ID 448: LED light generic error',
        '1C1' : 'ID 449: LED light EEPROM error',
        '1C2' : 'ID 450: LED light error in system',
        '1C3' : 'ID 451: LED light configuration',
        '1C4' : 'ID 452: LED light calibration',
        '1C5' : 'ID 453: LED light SD card error.',
        '1C6' : 'ID 454: LED light error in firmware',
        '1C7' : 'ID 455: LED light error in firmware',
        '1C8' : 'ID 456: LED light error in firmware',
        '1C9' : 'ID 457: LED light colour sensor',
        '1CA' : 'ID 458: LED light temperature',
        '1CB' : 'ID 459: LED light temperature',
        '1CC' : 'ID 460: LED light temperature',
        '1CD' : 'ID 461: LED light temperature',
        '1CE' : 'ID 462: LED light colour channel',
        '1CF' : 'ID 463: LED light colour channel',
        '1D0' : 'ID 464: LED light colour channel',
        '1D1' : 'ID 465: LED light colour channel',
        '1D2' : 'ID 466: LED light colour channel',
        '1D3' : 'ID 467: LED light colour channel',
        '1D4' : 'ID 468: LED light colour channel',
        '1D5' : 'ID 469: LED light colour channel'
    } 
    if hexID in errorCodes:
        return errorCodes[hexID].replace(' ','_').replace(':',''), True
        
    return None, False

# update the serial number into the data folder
def updateSerialNo(serial):
    with open('/home/User1/msV2/data/serial.txt', 'w') as serialFile:
        serialFile.write(serial)
        serialFile.close()


