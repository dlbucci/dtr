#/usr/bin/env bash

hcitool scan
sudo rfcomm release 0
sudo rfcomm bind /dev/rfcomm0 98:D3:31:80:40:AE # robot 0
sudo chmod o+rw /dev/rfcomm0
