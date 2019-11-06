#!/bin/bash
/home/User1/emsa/cleariptables
echo "Cleared Iptables"
# record password
PASS="1234"
deviceName=$(hostname)

# variables
country="US"
state="NC"
locality="CLT"
organization="Kavo Kerr"
organizationalunit="Product Development"
email="luke.garceau@kavokerr.com"
password="1234"


sudo apt-get update --fix-missing
yes | sudo apt --fix-broken install

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

# install openssl
yes | sudo apt-get install openssl
sudo chown User1:User1 *
echo "Installed Openssl"
# create new cert
openssl req -newkey rsa:2048 -keyform PEM -keyout $deviceName.key -out $deviceName.req -passout pass:"1234" -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$deviceName/emailAddress=$email"
echo "Created Request"
# register the cert with the root CA
openssl x509 -req -in $deviceName.req -CA rootCA.pem -CAkey rootCAKey.pem -set_serial 101 -extensions client -days 5000 -outform PEM -out $deviceName.pem -passin pass:"1234" 
echo "Created and Signed the certificate"

# remove root ca from device
rm -f rootCAKey.pem 
rm -f rootCA.pem
export AWS_CONFIG_FILE=/home/User1/aws-script/config.txt
export AWS_PROFILE=luke.garceau
aws s3 rm s3://dhr-kkg-tu/Downloads/$deviceName/rootCAKey.pem
aws s3 rm s3://dhr-kkg-tu/Downloads/$deviceName/rootCA.pem
echo "Removed Root Certs"

yes | sudo apt-get install git
cd /home/User1/
git clone https://lgarceau768:Spook524*@github.com/lgarceau768/msV2.git

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

systemctl status msIot -l >> msInstallFirstLaunch.log
mv msInstallFirstLaunch.log /home/User1/out/

iptables-save > /etc/iptables/rules.v4
shutdown -r +2
aws s3 rm s3://dhr-kkg-tu/Downloads/$deviceName/connectToIotc.sh
python3 /home/User1/msV2/dist/registerX509.py
echo "Running the register x509"

