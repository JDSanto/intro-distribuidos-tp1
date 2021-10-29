#!/bin/bash

# Para poder ejecutar comcast en modo no interactivo
# echo "$(whoami) ALL=NOPASSWD: $(which tc), $(which iptables), $(which ip6tables)" | sudo tee /etc/sudoers.d/99-comcast

OUTPUT=times.csv
rm $OUTPUT

for i in 0 5 10 20; do
	"${COMCAST:-comcast}" --device lo --stop 2>&1 > /dev/null
	"${COMCAST:-comcast}" --device lo --packet-loss=${i}% 2>&1 > /dev/null
	if [ $? -ne 0 ]; then
		break
	fi
	
	echo "Packet loss: ${i}%"
	
	for p in "tcp" "udp+saw" "udp+gbn"; do
		RESULTS=$OUTPUT PLOSS=$i ./test-connection.sh $p
	done; 
done;

"${COMCAST:-comcast}" --device lo --stop 2>&1 > /dev/null

echo -e "Packet Loss;File Size;Protocol;Operation;Time;Error\n$(sort -hr ${OUTPUT})" > $OUTPUT
