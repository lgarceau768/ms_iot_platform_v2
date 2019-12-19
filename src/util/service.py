import os, sys, json


def HTD(hexStr):
    hexStr = hexStr.lower()
    if hexStr[0] == 'a': f = 10
    elif hexStr[0] == 'b': f = 11
    elif hexStr[0] == 'c': f = 12
    elif hexStr[0] == 'd': f = 13
    elif hexStr[0] == 'e': f = 14
    elif hexStr[0] == 'f': f = 15
    else: f = int(hexStr[0])
    if hexStr[1] == 'a': s = 10
    elif hexStr[1] == 'b': s = 11
    elif hexStr[1] == 'c': s = 12
    elif hexStr[1] == 'd': s = 13
    elif hexStr[1] == 'e': s = 14
    elif hexStr[1] == 'f': s = 15
    else: s = int(hexStr[1])
    return  (f*16)+s

def jsonConvert(key, value):
    return "{'%s':'%s'}" % (str(key), str(value))

def parseData(data):
    # seperate
    canID = data[1].strip().replace('ID:','').replace(' ','')
    timestamp = data[0]
    data = data[2].strip().split(' ')
    #del data[0] when using csv file
    messages = []

    # 0x60 and 0x61 are the main codes
        # 0x60 is a request and 0x61 is a response
        
        ### Version Query 

    # Version Query 1
    if canID == '0x60':
        if data[0] == '01' and data[1] == '01':
            messages.append(jsonConvert('versionQuery','service mode 1'))
            messages.append(jsonConvert('versionQuery', 'service mode 1 version request 1'))
    if canID == '0x61':
        if data[0] == '01' and data[1] == '01':
            messages.append(jsonConvert('versionQuery1','service mode 1 response'))
            messages.append(jsonConvert('versionQuery1','service mode 1 version request 1 response'))
            # now based off what data[2] is we can determine the version of the unit
            # have no clue what the other data bytes mean
            # Data[2] = Version of first character
            # Data[3] = Version of second character
            # Data[4] = Version of third character
            # Data[5] = Version of fourth character
            # Data[6] = Version date 10th day
            # Data[7] = Version date 1st day
            messages.append(jsonConvert('versionQuery1Data', data))

    # Version Query 2
    if canID == '0x60':
        if data[0] == '01' and data[1] == '02':
            messages.append(jsonConvert('versionQuery2','service mode 1'))
            messages.append(jsonConvert('versionQuery2','service mode 1 version request 2'))
    if canID == '0x61':
        if data[0] == '01' and data[1] == '02':
            messages.append(jsonConvert('versionQuery2','service mode 1 response'))
            messages.append(jsonConvert('versionQuery2','service mode 1 version request  2 response'))
            # Data[2] = Version date 10th month
            # Data[3] = Version date 1st month
            # Data[4] = Version date 1000 year
            # Data[5] = Version date 100 year
            # Data[6] = Version date 10 year
            # Data[7] = Version date 1 year
            messages.append(jsonConvert('versionQuery2Data', data))
    
    ### Key Test

    # Button Query 1
    if canID == '0x60':
        if data[0] == '02' and data[1] == '01':
            messages.append(jsonConvert('buttonQuery1','service mode 2'))
            messages.append(jsonConvert('buttonQuery1','service mode 2 key inquiry 1'))
    if canID == '0x61':
        if data[0] == '02' and data[1] == '01':
            messages.append(jsonConvert('buttonQuery1','service mode 2 response'))
            messages.append(jsonConvert('buttonQuery1','service mode 2 key inquiry 1 response'))
            # Data[2] = keys_G.Fussanl
            # Data[3] = keys_G.H2OIn1
            # Data[4] = keys_G.H2OIN
            # Data[5] = keys_G.key0
            # Data[6] = keys_G.key2
            # Data[7] = keys_G.key4
            messages.append(jsonConvert('buttonQuery1Data', data))
    
    # Button Query 2
    if canID == '0x60':
        if data[0] == '02' and data[1] == '02':
            messages.append(jsonConvert('buttonQuery2','service mode 2'))
            messages.append(jsonConvert('buttonQuery2','service mode 2 key inquiry 2'))
    if canID == '0x61':
        if data[0] == '02' and data[1] == '02':
            messages.append(jsonConvert('buttonQuery1','service mode 2 response'))
            messages.append(jsonConvert('buttonQuery1','service mode 2 key inquiry 2 response'))
            # Data[2] = keys_G.H_Abl
            # Data[3] = keys_G.chair
            # Data[4] = keys_G.In0
            # Data[5] = keys_G.In1
            # Data[6] = keys_G.In2
            # Data[7] = keys_G.In3
            messages.append(jsonConvert('buttonQuery2Data', data))
        
    
    ### Driver Test
    
    # Driver Query 1
    if canID == '0x60':
        if data[0] == '03' and data[1] == '01':
            messages.append(jsonConvert('driverQuery1','service mode 3'))
            messages.append(jsonConvert('driverQuery1','service mode 3 driver query 1'))
    if canID == '0x61':
        if data[0] == '03' and data[1] == '01':
            messages.append(jsonConvert('driverQuery1','service mode 3 response'))
            messages.append(jsonConvert('driverQuery1','service mode 3 driver query 1 response'))
            # Data[2] = Driver.Unit0
            # Data[3] = Driver.Unit1
            # Data[4] = Driver.Unit2
            # Data[5] = Driver.Unit3
            # Data[6] = Driver.Unit4
            # Data[7] = Driver.TrH2O
            messages.append(jsonConvert('driverQuery1', data))

    # Driver Query 2
    if canID == '0x60':
        if data[0] == '03' and data[1] == '02':
            messages.append(jsonConvert('driverQuery2','service mode 3'))
            messages.append(jsonConvert('driverQuery2','service mode 3 driver query 2'))
    if canID == '0x61':
        if data[0] == '03' and data[1] == '01':
            messages.append(jsonConvert('driverQuery1','service mode 3 response'))
            messages.append(jsonConvert('driverQuery1','service mode 3 driver query 2 response'))
            # Data[2] = Driver.LED0
            # Data[3] = Driver.LED1
            messages.append(jsonConvert('driverQuery1', data[2] + ' ' + data[3]))
    
    ### Show and Save Flag Bits
    if canID == '0x60':
        if data[0] == '04' and data[1] == '01':
            messages.append(jsonConvert('flagBytes', 'service mode 4'))
            messages.append(jsonConvert('flagBytes', 'request of the flag bytes'))
            # Data[2].= flag byte 1
            # Data[3].= flag byte 2
            # Data[4].= flag byte 3
            # Data[5] = Save flag byte 1..5
            # Data[6].= flag byte 4
            # Data[7].= flag byte 5

            # Data[5] = 1 : Save flag byte 1
            # Data[5] = 1 : Save flag byte 2
            # Data[5] = 1 : Save flag byte 3
            # Data[5] = 1 : Save flag byte 4
            # Data[5] = 1 : Save flag byte 5
            messages.append(jsonConvert('flagBytesData', data))
    if canID == '0x61':
        if data[0] == '04' and data[1] == '01':
            messages.append(jsonConvert('flagBytes', 'service mode 4 response'))
            messages.append(jsonConvert('flagBytes', 'send service mode 4 flag bytes'))
            # Data[2].= flag byte 1
            # Data[3].= flag byte 2
            # Data[4].= flag byte 3
            # Data[5] = 0x00
            # Data[6].= flag byte 4
            # Data[7].= flag byte 5
            messages.append(jsonConvert('flagBytesDataResponse',data))

    ### Display and set tumbler full and rinsing time

    # Request 1
    if canID == '0x60':
        if data[0] == '06' and data[1] == '01':
            messages.append(jsonConvert('tumblerBowlRequest1', 'service mode 6'))
            messages.apennd(jsonConvert('tumblerBowlRequest1', 'request 1: request times'))
    if canID == '0x61':
        if data[0] == '06' and data[1] == '01':
            messages.append(jsonConvert('tumblerBowlRequest1', 'service mode 6 response'))
            messages.append(jsonConvert('tumblerBowlRequest1', 'inquiry 1'))
            
            # tumblr filling time convert hex to dec\
            decimal = HTD(data[2])
            messages.append(jsonConvert('tumblerBowlRequest1Tumbler',decimal))

            # bowl rinising time convert hex to dec
            decimal = HTD(data[3])
            messages.append(jsonConvert('tumblerBowlRequest1Bowl',decimal))
        
    # Request 2 & 3
    if canID == '0x60':
        if data[0] and '06' and data[1] == '02':
            messages.append(jsonConvert('tumblerBowlRequest2', 'serivce mode 6'))
            messages.append(jsonConvert('tumblerBowlRequest2', 'inquiry 2'))
            # tumblr filling time convert hex to dec
            decimal = HTD(data[2])
            messages.append(jsonConvert('tumblerBowlRequest2Tumbler',decimal))
        if data[0] and '06' and data[1] == '03':
            messages.append(jsonConvert('tumblerBowlRequest3', 'serivce mode 6'))
            messages.append(jsonConvert('tumblerBowlRequest3', 'inquiry 3'))
            # tumblr filling time convert hex to dec
            decimal = HTD(data[2])
            messages.append(jsonConvert('tumblerBowlRequest3Bowl',decimal))
    
    ### Germ Reduction

    # All Requests
    if canID == '0x60':
        if data[0] == '07':
            requestNum = int(data[1][1])
            requestMessage = 'germReductRequest%i' % requestNum
            messages.append(jsonConvert(requestMessage, 'service mode 7'))
            if data[1] == '01':
                messages.append(jsonConvert(requestMessage, 'request 1: request days since last germ reduction'))
            # 2 - 7 just reply with inquiry#
            inquiryNum = int(data[1][1])
            if inquiryNum >= 2 and inquiryNum <= 7:
                messages.append(jsonConvert(requestMessage, 'inquiry %i' % inquiryNum))
    if canID == '0x61':
        if data[0] == '07':
            inquiryNum = int(data[1][1])
            inquiryMessage = 'inquiry %i' % inquiryNum
            requestMessage = 'germReductResponse%i' % inquiryNum
            messages.append(jsonConvert(requestMessage, inquiryMessage))
            messages.append(jsonConvert(requestMessage, 'service mode 7'))
            if data[1] == '01':
                daysSince = int(data[2])*256
                messages.append(jsonConvert(requestMessage+'DaysSinceGerm1', daysSince))
                messages.append(jsonConvert(requestMessage+'DaysSinceGerm2', data[3]))
            if data[1] == '02':
                daysSince = int(data[2])*256
                messages.append(jsonConvert(requestMessage+'IntervalsSinceGerm1', daysSince))
                messages.append(jsonConvert(requestMessage+'IntervalsSinceGerm2', data[3]))
            if data[1] == '04':
                daysSince = int(data[2])*256
                messages.append(jsonConvert(requestMessage+'NumberPerformed1', daysSince))
                messages.append(jsonConvert(requestMessage+'NumberPerformed2', data[3]))
            if data[1] == '06':
                messages.append(jsonConvert(requestMessage+'Oxygenal Concentration',data[2]))
    
    ### Service

    # All Request
    if canID == '0x60':
        if data[0] == '08':
            serviceNo = int(data[1][1])
            keyVal = 'serviceRequest%i' % serviceNo
            messages.append(jsonConvert(keyVal, 'service mode 8'))
            if data[1] == '01':
                messages.append(jsonConvert(keyVal, 'request 1 : request days since last service'))
            if data[1] == '02':
                messages.append(jsonConvert(keyVal, 'inquiry 2'))
            if data[1] == '03':
                messages.append(jsonConvert(keyVal, 'request 1 : request days since last service'))
                messages.append(jsonConvert(keyVal+'ServiceIntervalSet', data[2]))
                # Data[2] = Set service interval when 6,12,18 or 24
    if canID == '0x61':
        if data[0] == '08':
            serviceNo = int(data[1][1])
            keyVal = 'serviceRequest%i' % serviceNo
            messages.append(jsonConvert(keyVal, 'service mode 8'))
            if data[1] == '01':
                messages.append(jsonConvert(keyVal, 'inquiry 1'))
                daysSince = int(data[2])*256
                messages.append(jsonConvert(keyVal+'DaysSinceLastService1', daysSince))
                messages.append(jsonConvert(keyVal+'DaysSinceLastService2', data[3]))
            if data[1] == '03':
                messages.append(jsonConvert(keyVal, 'inquirt 3'))
                messages.append(jsonConvert(keyVal+'ServiceIntervalResponse', data[2]))
                # Data[2] = Service interval (6,12,18,24 months)
    
    ### Display Boiler Temp and Set Correction Value

    # Request 1
    if canID == '0x60':
        if data[0] == '09' and data[1] == '01':
            messages.append(jsonConvert('boilerTemp','service mode 9'))
            messages.append(jsonConvert('boilerTemp', 'request 1 : Request/Save boiler temperature'))
            # it says if value is between 35 and 45 but not sure if that is decimal or hex
            hexVal = HTD(data[2])
            if hexVal > 35 and hexVal < 45:
                messages.append(jsonConvert('boilerTempSet', hexVal))
            else:
                messages.append(jsonConvert('boilerTempSet', 'value not btw 35 and 45'))
    if canID == '0x61':
        if data[0] == '09' and data[1] == '01':
            messages.append(jsonConvert('boilerTempResponse', 'service mode 9'))
            messages.append(jsonConvert('boilerTempResponse', 'inquiry 1'))
            messages.append(jsonConvert('boilerTargetPotVal', HTD(data[2])))
            messages.append(jsonConvert('boilterActualPotVal', HTD(data[3])))
            messages.append(jsonConvert('boilerStartedPot', data[4]))
    

    ### Display and Set Maximum number of Dentists

    # Request 1
    if canID == '0x60':
        if data[0] == '0B':
            if data[1] == '01':
                messages.append(jsonConvert('maxDentists', 'service mode B'))
                messages.append(jsonConvert('maxDentists', 'request 1: request/save number of dentists'))
                number = int(data[2])
                if number >= 1 and number <= 6:
                    messages.append(jsonConvert('maxDentistsSet', numer))
                else:
                    messages.append(jsonConvert('maxDentistsSet', 'value not between 1 and 6'))
    if canID == '0x61':
        if data[0] == '0B':
            if data[1] == '01':
                messages.append(jsonConvert('maxDentistsResponse', 'service mode B'))
                messages.append(jsonConvert('maxDentistsResponse', 'inquiry 1'))
                number = int(data[2])
                messages.append(jsonConvert('maxDentistsResponseTotal', number))
    

    ### Display and Set Correction value of the 1410C

    # Request
    if canID == '0x60':
        if data[0] == '0D':
            messages.append(jsonConvert('correctionValueRequest', 'service mode D'))
            message = ''
            if data[1] == '01':
                message = 'request correction value'
            if data[1] == '02':
                message = 'accept correction value from data[2] when value <= 50'
            if data[1] == '03':
                message = 'save correction value'
            messages.append(jsonConvert('correctionValueRequest', message))
            messages.append(jsonConvert('correctionValueValue', data[2]))
    if canID == '0x61':
        if data[0] == '0D':
            if data[1] == '01':
                messages.append(jsonConvert('correctionValueResponse', 'service mode D'))
                messages.append(jsonConvert('correctionValueResponse', 'inquiry 1'))
                messages.append(jsonConvert('correctionValueValue', data[2]))
    

    ### Display and set instrument data
    
    # Request
    if canID == '0x60':
        if data[0] == '0E':
            message = ''
            messages.append(jsonConvert('instrumentData', 'service mode E'))
            if data[1] == '01':
                message = 'request values'
            if data[1] == '02':
                message = 'save afterglow time'
            if data[1] == '03':
                message = 'save lux assistant correction value'
            if data[1] == '04':
                message = 'save zeg correciton value'
            if data[1] == '05':
                message = 'save lux dentist correction value'
            messages.append(jsonConvert('instrumentDataAction', message))
            messages.append(jsonConvert('instrumentDataAfterGlow', data[2]))
            messages.append(jsonConvert('instrumentDataCorrectionValueLuxAssistant', data[3]))
            messages.append(jsonConvert('instrumentDataCorrectionValueZEG', data[4]))
            messages.append(jsonConvert('instrumentDataCorrectionValueLuxDentist', data[5]))
    if canID == '0x61':
        if data[0] == '0E':
            if data[1] == '01':
                messages.append(jsonConvert('instrumentData', 'serivce mode E'))
                messages.append(jsonConvert('instrumentData', 'inquiry 1'))
                messages.append(jsonConvert('instrumentDataCorrectionValue1410C', data[2]))
    

    ### Reading and manipulating EEPROM and RTC Unit

    # Request 1,2,5,6
    if canID == '0x60':
        if data[0] == '0F':
            messages.append(jsonConvert('eeprom', 'service mode F'))
            message = ''
            if data[1] == '01' or data[1] == '05':
                message = 'request value'
            if data[1] == '02' or data[1] == '06':
                message = 'save value'
            messages.append(jsonConvert('eeprom', message))
            messages.append(jsonConvert('eepromHighAddress', data[2]))
            messages.append(jsonConvert('eepromLowAddress', data[3]))
            messages.append(jsonConvert('eepromValSave', data[4]))
    if canID == '0x61':
        if data[0] == '0F' and data[1] == '01':
            messages.append(jsonConvert('eeprom', 'service mode F'))
            messages.append(jsonConvert('eeprom', 'inquiry 1'))
            messages.append(jsonConvert('eepromValue', data[2]))
        if data[0] == '0F' and data[1] == '05':
            messages.append(jsonConvert('eeprom', 'service mode F'))
            messages.append(jsonConvert('eeprom', 'inquiry 5'))
            messages.append(jsonConvert('eepromValueRTC', data[2]))
        


    ### Show unit power supplies
    if canID == '0x60':
        if data[0] == '10' and data[1] == '01':
            messages.append(jsonConvert('powerSupplies','service mode 0x10'))
            messages.append(jsonConvert('powerSupplies', 'query values'))
    if canID == '0x61':
        if data[0] == '10':
            messages.append(jsonConvert('powerSupples', 'service mode 0x10'))
            message = ''
            if data[1] == '01':
                message = 'supply voltage 5Vext'
            if data[1] == '02':
                message = 'supply voltage 5V'
            if data[1] == '03':
                message = 'supply voltage 7V'
            if data[1] == '04':
                message = 'supply voltage 24V'
            if data[1] == '05':
                message = 'supply voltage 33V'
            messages.append(jsonConvert('powerSupplies', message))
            messages.append(jsonConvert('powerSuppliesActualValueMSN', data[2]))
            messages.append(jsonConvert('powerSuppliesActualValueLSN', data[3]))
            messages.append(jsonConvert('powerSuppliesMinimumMSN', data[4]))
            messages.append(jsonConvert('powerSuppliesMinimumLSN', data[5]))
            messages.append(jsonConvert('powerSuppliesMaximumMSN', data[6]))
            messages.append(jsonConvert('powerSuppliesMaximumLSN', data[7]))
    return messages


