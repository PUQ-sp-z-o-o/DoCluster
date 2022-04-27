#!/bin/bash
# DoCluster installation wrapper
# http://ducluster.com

# Am I root?
if [ "x$(id -u)" != 'x0' ]; then
    echo 'Error: this script can only be executed by root'
    exit 1
fi


apt-get install git -y
apt-get install python3-pip -y
apt-get install python3-venv -y
git clone https://github.com/PUQ-sp-z-o-o/DoCluster
cd /root/DoCluster/
python3 -m venv .venv
git pull
pip3 install -r requirements.txt

exit
