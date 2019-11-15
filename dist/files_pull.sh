#!/bin/bash
/home/User1/emsa/cleariptables
systemctl stop monitor
systemctl stop msIot
cd /home/User1/ms_aws_monitor/
git stash
git pull https://lgarceau768:Spook524*@github.com/lgarceau768/ms_aws_monitor.git
cd ../msV2
git stash
git pull https://lgarceau768:Spook524*@github.com/lgarceau768/msV2.git
systemctl start monitor
systemctl start msIot

