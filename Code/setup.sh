#!/bin/bash

# cleanup() {
#     echo "Cleaning up..."
#     # Kill all background processes started by this script
#     pkill -P $$
# }
#
# # Trap signals for cleanup
# trap cleanup EXIT

clear
sleep 5
rm -f  signal.flag
rm -f donepart
num_experts=${1:-4} # Starting From 0

# Start manager.py in the background
echo "Valu of Expert"
echo $num_experts
#konsole --noclose -e python3 manager.py &
#manager_pid=$! 
python3 manager.py &

while [ ! -f donepart ]; do
    sleep 1
done
sleep 2
# Start expert processes in the background
for i in $(seq 0 $num_experts); do
    echo "[SHELL] Starting Expert $i"
    #konsole --noclose -e python3 expert.py $i &
    python3 expert.py $i &
    sleep 1
done

# Wait for manager.py to finish
wait_time=0
while [ ! -f "signal.flag" ];
do
    sleep 1
    wait_time=$((wait_time +1))
    if [ $wait_time -ge 1500 ];
    then
        kill $(jobs -p)
        sleep 5
        exit 1
    fi
done
#kill $(jobs -p)
sleep 5


