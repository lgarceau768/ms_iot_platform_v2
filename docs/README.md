# Kavo MS IoT Platform

> Version: _2.0_  
> Author:  _Luke Garceau_  

## Requirements

1. Read CAN messages in real-time
2. Convert the given variables to engineering useful variables

        - useTime
        - runTime
        - idleTime
        - hygieneCycle Data
        - error messages
        - location data
3. Keep the device updated with its cloud counterpart

        - Start MS service on startup
        - Verify MS continues to run
        - Reestablish connection losses from lost wifi
        - Collects data generated during connection losses and transfers the data when connections are reestablished
4. Send engineered variables to Iot Central
5. Dynamically update IP tables with correct MS IP addresses

# Overall Concept
1. Connect to Iot Central and Initialize Can Bus
2. Split each task into a seperate Thread  
3. Run the Threads using parallelism  
> _Parallelism is the idea of running multiple processes at the same time_  
> _Transfer of data between each process is acheived by shared mutex variables (aka constant variables that each thread has access to)_  
4. Shared Variables
        
        - const.CAN_DATA
        - const.CAN_CODES
        - const.MSG_TO_SEND
        - const.MSG_TO_RECORD
# Pseudo Code

## Shared Variables
- __const.CAN_DATA__  
        - Starts in `readCan.py -> readData()`  
        - List of tuple variables that are to be interpretted into english  
        - Ends in `hexToEng.py -> interpret()`
- __const.MSG_TO_SEND__  
        - Starts in `hexToEng.py -> interpret()`  
        - List of arrays formatted like:        
        `[`    
        `['runTime',  '0.008333333333333333']`  
        `]`  
        __or__  
        `[`  
        `['runTime', '0.008333333333333333']`   
        `,` __(comma seperated)__  
        `['timestamp', '2019-11-06T03:40:29.863497']`  
        `['hygieneLast', '-1']`  
        `['hygieneType', 'no_mem']`  
        `['hygieneStart', 'no_mem']`  
        `['hygieneStop', 'no_mem']`  
        `]`  
        - Can have multiple messages  
        - Ends in `sendIotc.py -> sendMessages()`
- __const.MSG_TO_RECORD__  
        - Starts in `hexToEng.py -> interpret() -> alreadyHave()`  
        - List of tuple variables to be written to the .csv file  
        - Ends in `recordData.py -> recordData()` 


## Read CAN Messages
1. Translate CAN Hex Code to format below:   
`Python Tuple of Strings Object`  
`(Timestamp, CanID, Message)`  
1. Append The Tuple to `const.MSG_TO_RECORD` shared program variable  
2. Append The Tuple to `const.MSG_TO_SEND` shared program variable

## Interpret Messages to Useful Variables
- _runTime_  
        - Sent every interval in `config.ini`  
- _useTime_ and _idleTime_  
        - Figured out using `hexToEng.py -> alreadyHave()`  
        - Sent every interval in `config.ini`  
- _hygiene data_  
        - Update message sent every interval in `config.ini`   
        - Records data to text file `start|stop|type -> data/hygieneData.txt`  
        - Sends `hygieneEvent` and updates data once a hygiene cycle is triggered on the chair  
        - ???What about the hygiene last message???
- _error messages_  
        - Sends an error message json variable everytime there is a new error message  
        - See `hexToEng.py -> interpret()` 
- _location data_  
        - Pulls user inputted data about the device from the device twin  
        - Cloud Properties

                - officeName
                - officeLocation
                - roomName
                - deviceName ???Is this pulled from the cloud or the device?? The device should already have a unique device name on it
- Remove the can message from `const.CAN_DATA`

## Record Data to .csv file
- Will record new can messages to the `.csv` file in `data/***.csv`
- Format of fileName:  (should match old format alpha010_11112019_133131.csv deviceID_mmddyyyy_hhmmss.csv)
        `deviceName = socket.gethostname()`  
        `timestamp = datetime.datetime.now()`  
        `timestamp = '%i-%i-%i_%i:%i' % (timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute)` 
        `fileName = '%s_canData_%s.csv' % (deviceName, timestamp)`
- Message needs to be of this format:  (should match old format 07/25/2019 18:31:08:031  ID: 0x08 Message: 00 06 c0 00 00 00 00 00 timestamp in 1 column, can message in 2nd column )
        `String:   `  
        `YYYY-MM-DD HH-MM-SS.MMMM ID: Ox### Message: ## ## ## ## ## ## ## ##`  
  - Syntax to format a Can Message:  
        ` incoming canMessage: data = (tuple of strings)`  
        `canTS = data[0]`  
        `canID = data[1]`  
        `canMG = data[2]`  
        `formatMsg = '%s\tID: %s\tMessage: %s\n' % (canTS, canID, canMG)`
- Remove the can message from `const.MSG_TO_RECORD`

## Send To Iot Central
1. Pull down the device twin from Iot Central
2. Send the init messages: ???Why are you sending mac, wireless mac and ip address??
        
        - Location Data: (officeName, roomName, officeLocation, deviceID)
        - Ip Address
        - Hardware Mac Address
        - Wireless Mac Address
        - deviceInit message
3. Loop through all messages in `const.MSG_TO_SEND`
4. Append the `deviceID` to each message
5. If `msg` in `property list: ['hygieneStart, hygieneStop', 'hygieneLast', 'batteryLevel', 'serialNum']`  
        - __True__: Send message as a property
        - __False__: Send message as telemetry
6. Send `lastTimeConnected` property
7. Remove message from `const.MSG_TO_SEND`

## Calculation / Determination of UseTime and IdleTime  (Im not sure I understand the logic.  It looks like it will only send Idle time)
I use a `deviceState` variable which is of data type `String`, which has 3 values

        - Use
        - Idle
        - IdlePending
  
__Scenario 1:__   


|Time (minutes since boot)| Whats Happening | deviceState  |
|-------|------------------------------|--------------|
| 0                                 | Device Boot                                 | N/A          |
| 1                                 | Device Reads initial new can codes/messages | Use          |
| 1+1ms                             | Device sees starts to see old can messages  | Idle Pending |
| 5 (use threshold)                 | Device sends useTime message                | Idle         |
| 12 (useThreshold + idlethreshold) | Device sends idleTime message               | Idle         |  

__Secnario 2:__


| Time (minutes since boot)         | Whats Happening                              | deviceState |
|-----------------------------------|----------------------------------------------|-------------|
| 0                                 | Device Boot                                  | N/A         |
| 1                                 | Device Reads initial new can codes/messages  | Use         |
| 1+1ms                             | Device sees starts to see old can messages   | IdlePending |
| 3                                 | New Can Message Comes through                | Use         |
| 3 cont.                           | UseTimeDelta updated   IdleTimeStart reset   | Use         |
| 3+1ms                             | Device sees old can id/message               | IdlePending |
| 5 (or useThreshold)               | Device sends useTime message                 | Idle        |
| 12 (useThreshold + idleThreshold) | Device sends idleTime message if no new code | Idle        |
