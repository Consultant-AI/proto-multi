#!/bin/bash

set -e

export DISPLAY=:${DISPLAY_NUM}
./xvfb_startup.sh
./tint2_startup.sh
./openbox_startup.sh
./x11vnc_startup.sh
