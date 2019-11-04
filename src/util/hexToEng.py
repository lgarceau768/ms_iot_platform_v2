import os, sys, asyncio, const as const, configparser, time, datetime
from util import rotatingLogger, hygieneData

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

    while True:
        compTimer = time.time()/60
        timestamp = datetime.datetime.now().isoformat()
        timestamp = ('timestamp', str(timestamp))
        messages = []
        # need to interpret the can data
        for data in const.CAN_DATA:
            if len(data) != 3:
                const.CAN_DATA.remove(data)
            # need to see if this is a new/old message
            else:
                # runtime
                runTimeDelta = abs(runTimeLast-compTimer)
                if runTimeDelta >= runTimeInt:
                    messages.append([('runTime', str(runTimeInt/60.0))])
                    runTimeLast = compTimer
                
                # hygiene
                hygieneTimeDelta = abs(hygieneTimeLast-compTimer)
                if hygieneTimeDelta >= hygieneTimeInt:
                    # need to read the old data
                    hygData = hygieneData.getHygieneInfo()
                    if 'no_mem' in hygData:
                        messages.append([timestamp, ('hygieneLast','-1'), ('hygieneType','no_mem'), ('hygieneStart','no_mem'), ('hygieneStop','no_mem')])
                    else:
                        start = hygData[0]
                        stop = hygData[1]
                        typeHyg = hygData[2]
                        # need to find difference in hours btw now and the last one
                        now = datetime.datetime.now()
                        then = datetime.datetime.strptime(str(stop), '%Y-%m-%d %H:%M:%S.%f')
                        diff = now-then
                        hours = int(diff.hour) + int(diff.day) * 24
                        hours = ('hygieneLast', str(hours))
                        messages.append([timestamp, hours, ('hygieneType', typeHyg), ('hygieneStart', start), ('hygieneStop', stop)])
                    hygieneTimeLast = compTimer
                
                # now use and idleTime
                whichTime = alreadyHave(data)
                idle = True
                use = False

                if whichTime == idle:
                    # idleTime
                    if deviceState == 'use':
                        idleTimeLast = compTimer
                        deviceState = 'idle'
                    idleTimeMsgDelta = abs(idleTimeLast-compTimer)
                    if idleTimeMsgDelta >= idleTimeInt:
                        idleTime = ('idleTime', str(idleTimeInt/60.0))
                        idleTimeLast = compTimer
                        messages.append([idleTime])
                else if whichTime == use:
                    if deviceState == 'idle':
                        useTimeLast = compTimer
                        deviceState = 'use'
                    useTimeDelta = abs(useTimeLast-compTimer)
                    if useTimeDelta >= useTimeInt:
                        useTimeLast = compTimer
                        messages.append([('useTime', str(useTimeInt/60.0))])

                             

# alreadyHave function - will return true of the message is already seen, retuyrn false if the message is new
# idle - true
# use - false
def alreadyHave(data):
    idle = True
    use = False
    for item in const.CAN_CODES:
        if item[1] == data[1]:
            # same can code
            item[0] = data[0]
            if item[2].strip().lower() == data[2].strip().lower():
                # the same can message
                return idle
            else:
                # new can message
                item[2] = data[2]
                return use
    const.CAN_CODES.append(data)
    return use