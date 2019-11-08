import os, sys, asyncio, const as const, configparser, time, datetime
from util import hygieneData
from util import rotatingLogger as logger, hygieneData

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

    # idletime
    idleTimeLast = compTimer
    idleTimeMsgDelta = abs(idleTimeLast-compTimer)
    idleTimeInt = float(config.get('Time', 'idleTime'))

    # usetime
    useTimeLast = compTimer
    useTimeDelta = abs(useTimeLast-compTimer)
    useTimeInt = float(config.get('Time', 'useTime'))

    # hygieneTime
    hygieneTimeLast = compTimer
    hygieneTimeDelta = abs(hygieneTimeLast-compTimer)
    hygieneTimeInt = float(config.get('Time', 'hygieneTime'))
    hygieneInProgress = False

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

                # for use need to remember when the last can message changed

                if whichTime == idle:
                    # idleTime
                    if deviceState == 'use':
                        idleTimeLast = compTimer
                        # make new deviceState for idlePending
                        deviceState = 'idle' 
                    idleTimeMsgDelta = abs(idleTimeLast-compTimer)
                    if idleTimeMsgDelta >= idleTimeInt:
                        # - set status to be in idle ONLY after the device has been in idle for the last X minutes
                        idleTime = ['idleTime', str(idleTimeInt/60.0)]
                        idleTimeLast = compTimer
                        messages.append([idleTime])
                        messages.append([timestamp, ['timeType', 'idleTime'], ['timeAmt', str(idleTimeInt/60.0)]])
                elif whichTime == use:
                    ##print('use')
                    #print('useCode: '+str(data))
                    const.CAN_DATA.append(data)
                    logger.get_logger().info('useCode: '+str(data))
                    if deviceState == 'idle':
                        useTimeLast = compTimer
                        deviceState = 'use'
                    useTimeDelta = abs(useTimeLast-compTimer)
                    if useTimeDelta >= useTimeInt:
                        useTimeLast = compTimer
                        messages.append([['useTime', str(useTimeInt/60.0)]])
                        messages.append([timestamp, ['timeType', 'useTime'], ['timeAmt', str(useTimeInt/60.0)]])

                    ### check for other codes as well
                    canID = data[1]
                    message = data[2].split(' ')
                    logger.get_logger().info(canID)
                    # errorMessage
                    if canID == '0x402':
                        logger.get_logger().info(str(message))
                        if message[2] != '00':
                            errorMessage = getErrorMessage(message)
                            if errorMessage[1] is True:
                                messages.append([['errorMessage', str(errorMessage[0])], ['controlByte', message[0]], timestamp])

                    # hygiene status
                    if canID == '0x08':
                        if message[5] != '80':                            
                            if message[4] == '88' and message[5] == '01' and not hygieneInProgress:
                                hygieneInProgress = True
                                hygType = ['hygieneType', 'in_progress']
                                hygStart = ['hygieneStart', datetime.datetime.now().isoformat()]
                                hygStop = ['hygieneStop', '']
                                hygieneData.setHygieneInfo(datetime.datetime.now().isoformat(), 'no_mem', 'no_mem')
                                hygLast = ['hygieneLast','0']
                                if not already:
                                    messages.append([timestamp, hygLast, hygType, hygStart, hygStop])
                                    messages.append([['hygieneEvent', 'started']])
                                    already = True
                            if message[5] == '00' and hygieneInProgress and (message[4] == '00' or message[4] == '01'):
                                hygieneType = ''
                                if message[4] == '00':
                                    hygieneType = 'germ_reduction'
                                elif message[4] == '01':
                                    hygieneType = 'intensive_germ_reduction'
                                hygieneInProgress = False
                                hygLast = ['hygieneLast', '0']
                                hygType = ['hygieneType', hygieneType]
                                hygStop = ['hygieneStop', datetime.datetime.now().isoformat()]
                                oldData = hygieneData.getHygieneInfo()
                                oldStart = oldData[0]
                                hygStart = ['hygieneStart', oldStart]
                                hygieneData.setHygieneInfo(oldStart, datetime.datetime.now().isoformat(), hygieneType)
                                if not already2:
                                    messages.append([timestamp, hygLast, hygType, hygStart, hygStop])
                                    messages.append([['hygieneEvent', 'started']])
                                    already2 = True
                                messages.append([timestamp, hygLast, hygType, hygStart, hygStop])
                                messages.append([['hygieneEvent', '%s_completed' % hygieneType]])
                    
                    # battery level
                    if canID == '0x08':
                        bt = message[7]
                        msg = ['batteryLevel', '']
                        if bt == '00':
                            msg[1] = 'n/a'
                        elif bt == '01':
                            msg[1] = 'full'
                        elif bt == '02':
                            msg[1] = 'half'
                        elif bt == '03':
                            msg[1] = 'low'
                        elif bt == '04':
                            msg[1] = 'critically_low'
                        else:
                            msg[1] = 'warning'
                        already = False
                        for msg in const.MSG_TO_SEND:                            
                            for item in msg:
                                if 'battery' in item[0]:
                                    already = True
                        if not already:
                            messages.append(msg)

                    # serial number
                    # if canID == '0x419' and message[0] == '06':
                    #     hexNum = str(message[3])+str(message[4])+str(message[5])+str(message[6])
                    #     srlNo = str(int(hexNum, 16))
                    #     serialNum =  ['serialNum', str(srlNo)]
                    #     messages.append([serialNum])  
            
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
        '20' : 'heartbeat gateway missing',
        '21' : 'can node missing',
        '22' : 'gateway eeprom error',
        '23' : 'can error',
        '24' : 'can error',
        '25' : 'can error',
        '26' : 'can error',
        '30' : 'chair learning a1 pot error',
        '31' : 'chair learning a2 pot error',
        '32' : 'chair a1 acknowledge error',
        '33' : 'chair a2 acknowledge error',
        '34' : 'i2c water block ack error',
        '35' : 'assistant element ack error',
        '36' : 'foot control battery',
        '37' : 'chair a3 acknowledge',
        '38' : 'please charge foot control battery',
        '39' : 'chair learning required',
        '3A' : 'unit timeout iic internal',
        '3B' : 'unit timeout iic external',
        '3F' : 'reset unit iic external',
        '40' : 'leaked water active',
        '41' : 'safety shut off bowl suction',
        '42' : 'amalgam serparator error',
        '43' : 'oxygenal empty',
        '44' : 'please perform service',
        '45' : 'intensive germ reduction required',
        '46' : 'deka bottle is empty',
        '47' : 'no oxgenal bottle',
        '48' : 'deka no bottle',
        '49' : 'low oxygenal level',
        '4A' : 'centra mat empty',
        '4B' : 'centra mat too full',
        '4C' : 'unit dc 24 exceeded by more than 10%',
        '4D' : 'more than 20% less than unit dc 24',
        '50' : 'safety shut off for chair',
        '51' : 'safety shut off for the chair',
        '53' : 'safety shut off on assistant element',
        '54' : 'safety shut off for spittoon bowl',
        '55' : 'safety shut off of stirrup switch',
        '60' : 'chair e30 chair learning required',
        '61' : 'chair e30 motor driver error',
        '62' : 'chair e30 motor driver overheating',
        '63' : 'chair e30 motor driver short circuiting',
        '64' : 'chair e30 eeprom error',
        '65' : 'chair e30 undervoltage/overvoltage',
        '68' : 'chair e30 vacustopp switch',
        '69' : 'chair e30 safety shut off kick plate',
        '6A' : 'chair e30 safety shut off backrest',
        '6B' : 'chair e30 safety shut off seat',
        '6C' : 'chair e30 safety shut off foot rest',
        '80' : 'reg data contr of unit missing',
        '81' : 'reg data contr dentist missing',
        '82' : 'reg data ims missing',
        '83' : 'reg data of led light missing',
        '84' : 'reg data contr unit missing',
        '85' : 'heartbeat contr unit missing',
        '86' : 'heartbeat contr dentist missing',
        '87' : 'heartbeat led light missing',
        '8C' : 'error during sd card init',
        '8D' : 'error during eeprom access',
        '8E' : 'error during ethernet access',
        '8F' : 'error during gateway software update',
        '90' : 'error during unit software update',
        '91' : 'error during dentist software update',
        '92' : 'error during ims software update',
        '93' : 'error in ergocom communication',
        '94' : 'error init config memory',
        '95' : 'error init error memory',
        '96' : 'firmware update set is faulty',
        '97' : 'invalid firmware combination',
        '98' : 'operation in debug mode',
        '9B' : 'ethernet link lost',
        '9C' : 'error access update files',
        '9D' : 'unexpected reset contr unit',
        '9E' : 'gateway can bus warn',
        'A0' : 'gateway can bus off',
        'A1' : 'invalid cms configuration',
        'A2' : 'lost connection to cms server',
        'A3' : 'no Response from cms server',
        'A4' : 'faulty cms server download',
        'A5' : 'cms server login failed',
        'A6' : 'reg data contro dentist missing',
        'A7' : 'reg data of led light missing',
        'A8' : 'error in fw update of led light',
        'A9' : 'led light generic error'
    } 

    if hexID in errorCodes:
        return errorCodes[hexID].replace(' ','_'), True
        
    return None, False