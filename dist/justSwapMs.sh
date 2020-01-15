#!/bin/bash
/home/User1/emsa/cleariptables
echo "Cleared Iptables"

sudo apt-get update --fix-missing
yes | sudo apt --fix-broken install
sudo apt-get install dnsutils
#### REGISTERING BULK REMOTE.IT

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

cd /home/User1/
git clone https://AAAAAAAAA:AAAAAA*@github.com/lgarceau768/msV2.git

# remove the old ms platform
rm -rf /home/User1/connected-treatment-units

cd /home/User1/aws-script/Downloads/
# install python3
yes | sudo apt-get install python3
echo "Installed Python3"

# install python3-pip
yes | sudo apt-get install python3-pip
echo "Installed Python3-pip"

# install the new preview sdk lib
python3 -m pip install azure-iot-device
python3 -m pip install getmac
python3 -m pip install python-can
echo "Installing the python preview sdk"

# make the certs dir
mkdir /home/User1/certs
mv $deviceName.key /home/User1/certs/
mv $deviceName.pem /home/User1/certs/

# move the service
mv -f /home/User1/msV2/dist/msIot.service /etc/systemd/system/msIot.service
systemctl enable msIot

# move the start script
tr -d '\15\32' < /home/User1/msV2/dist/startMs.sh > /etc/systemd/system/startMs.sh

systemctl start msIot

systemctl status msIot -l >> swampMs.log
mv swampMs.log /home/User1/out/


