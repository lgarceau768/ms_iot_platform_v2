# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


# This is for illustration purposes only. The sample will not work currently.

import os
import asyncio
import socket
import sys
from azure.iot.device import X509
from azure.iot.device.aio import ProvisioningDeviceClient

hostname = socket.gethostname()

provisioning_host = "global.azure-devices-provisioning.net"
id_scope = "0ne0007906C"
registration_id = hostname



async def main():
    async def register_device():
        x509 = X509(
            cert_file = "/home/User1/certs/%s.pem" % hostname,
            key_file = "/home/User1/certs/%s.key" % hostname,
            pass_phrase = "1234" 
        )
        provisioning_device_client = ProvisioningDeviceClient.create_from_x509_certificate(
            provisioning_host=provisioning_host,
            registration_id=registration_id,
            id_scope=id_scope,
            x509=x509,
        )
        try:
            print('at return await -----------------')
            val = await provisioning_device_client.register()
            print('after await ------------')
            return val
        except Exception as e:
            print(str(e))
            sys.exit(0)

    try:
        results = await asyncio.gather(register_device())
    except Exception as e:
        print(str(e))
        sys.exit(0)
    registration_result = results[0]
    print("The complete registration result is")
    print(registration_result.registration_state)
    


if __name__ == "__main__":
    
    asyncio.run(main())

    # If using Python 3.6 or below, use the following code instead of asyncio.run(main()):
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()
