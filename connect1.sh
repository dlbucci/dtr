#/usr/bin/env bash

hcitool scan
sudo rfcomm release 1
sudo rfcomm bind /dev/rfcomm1 98:D3:31:60:1B:A1 # robot 1
sudo chmod o+rw /dev/rfcomm1
