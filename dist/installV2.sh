#!/bin/bash

# Pseudo Code

# clear iptables
/home/User1/emsa/cleariptables


# We want to wait until there is network connectivity
while ! ping -c 1 8.8.8.8; do
    echo "Waiting for 8.8.8.8 - network interface might be down..."
    sleep 1
done

# get name of the device
deviceName=$(hostname)

# repair linux files
sudo apt-get update --fix-missing
yes | sudo apt --fix-broken install

# install dependencies (apt-get)
yes | sudo apt-get install openssl
yes | sudo apt-get install dnsutils
yes | sudo apt-get install git
yes | sudo apt-get install python3
yes | sudo apt-get install python3-pip

# install dependencies (python -m pip)
python3 -m pip install azure-iot-device
python3 -m pip install getmac
python3 -m pip install python-can
python3 -m pip install psutil

# clone repositories
#Remove old
rm -rf /home/User1/connected-treatment-units

#MSV2
cd /home/User1/
git clone https://AAAAAAAAA:AAAAAA*@github.com/lgarceau768/msV2.git

#Monitor
cd /home/User1
git clone https://AAAAAAAAA:AAAAAA*@github.com/lgarceau768/ms_aws_monitor.git

# generate openssl cert
#Openssl variables
pass="1234"
country="US"
state="NC"
locality="Charlotte"
organization="Kavo Kerr"
unit="R&D"
email="luke.garceau@kavokerr.com"

cd /home/User1/aws-script/Downloads/
sudo chown User1:User1 *
openssl req -newkey rsa:2048 -keyform PEM -keyout $deviceName.key -out $deviceName.req -passout pass:"1234" -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$unit/CN=$deviceName/emailAddress=$email"
openssl x509 -req -in $deviceName.req -CA rootCA.pem -CAkey rootCAKey.pem -set_serial 101 -extensions client -days 5000 -outform PEM -out $deviceName.pem -passin pass:"1234" 
#Remove old cert files
rm -f rootCAKey.pem
rm -f rootCA.PEM

#Remove from aws
export AWS_CONFIG_FILE=/home/User1/aws-script/config.txt
export AWS_PROFILE=luke.garceau
aws s3 rm s3://dhr-kkg-tu/Downloads/$deviceName/rootCAKey.pem
aws s3 rm s3://dhr-kkg-tu/Downloads/$deviceName/rootCA.pem

# send bulk info to remote.it
#Bulk rIt variables
idCode=7880114B-945F-2D1D-5340-0E77725620E5

#change the mac ids in the options file
sed -i 's/REG_ID_ADAPTER="wlan0"/REG_ID_ADAPTER="eth1"/g' /usr/bin/connectd_options
sed -i 's/REG_KEY_ADAPTER="eth0"/REG_KEY_ADAPTER="eth1"/g' /usr/bin/connectd_options

#send bulk code to the txt file
echo $idCode > /etc/connectd/bulk_identification_code.txt

#Remove other files
rm -f /etc/connectd/registration_key.txt
rm -f /etc/connectd/registration_key.txt

#Enable the service
systemctl enable connectd
systemctl enable connectd_channel

#output the macinfo
ip -br link > $deviceNamemacInfo.log

# create service .sh files to be run with an lf file ending
#MSV2
echo "#!/bin/bash" > /etc/systemd/system/startMs.sh
echo "cd /home/User1/msV2/src" >> /etc/systemd/system/startMs.sh
echo "python3 main.py" >> /etc/systemd/system/startMs.sh
chmod 775 /etc/systemd/system/startMs.sh
#Monitor
echo '#!/bin/bash' > /home/User1/ms_aws_monitor/src/runService.sh
echo 'cd /home/User1/ms_aws_monitor/src' >> /home/User1/ms_aws_monitor/src/runService.sh
echo 'python3 monitor.py' >> /home/User1/ms_aws_monitor/src/runService.sh
chmod 775 /home/User1/ms_aws_monitor/src/runService.sh

# move service files
mv -f /home/User1/msV2/dist/msIot.service /etc/systemd/system/msIot.service
mv /home/User1/ms_aws_monitor/dist/monitor.service /etc/systemd/system/

#enable both
systemctl enable msIot
systemctl enable monitor

# run the registerX509 python file
#schedule shutdown
shutdown -r +5
python3 /home/User1/msV2/dist/registerX509.py