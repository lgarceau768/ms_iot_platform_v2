#!/bin/bash
BULK_ID_CODE=7880114B-945F-2D1D-5340-0E77725620E5 # <- subject to change
# registration id is the mac address from eth1
REG_ID="eth1"
# registraction key is the mac address from wlan0
REG_KEY="wlan0"
# need to modify the corresponding lines in the /usr/bin/connectd_options
# need to figure out how to do
sed -i 's/REG_ID_ADAPTER="wlan0"/REG_ID_ADAPTER="eth1"/g' /usr/bin/connectd_options
sed -i 's/REG_KEY_ADAPTER="eth0"/REG_KEY_ADAPTER="eth1"/g' /usr/bin/connectd_options

# modify the file /etc/connectd/bulk_identification_code.txt to just have the bulk config code
echo $BULK_ID_CODE > /etc/connectd/bulk_identification_code.txt
# delete the files /etc/connectd/hardware_id.txt
rm -f /etc/connectd/hardware_id.txt
# delete the files /etc/connectd/registration_key.txt
rm -f /etc/connectd/registration_key.txt
# register remote.it to run on startup

# run connected startupd on startup
systemctl enable connectd
systemctl enable connectd_schannel

# output the red it and reg key to a txt file
ip -br link > $(hostname)macinfo.log
mv $(hostname)macinfo.log /home/User1/out/
