#!/bin/bash
systemctl stop hostapd
systemctl disable hostapd

ifconfig wlan0 0.0.0.0
sed -i 's/^nohook wpa_supplicant/#nohook wpa_supplicant/'  /etc/dhcpcd.conf
sed -i 's/^static ip_address=192.168.63.1\/24/#static ip_address=192.168.63.1\/24/'  /etc/dhcpcd.conf
sed -i 's/^interface wlan0/#interface wlan0/'  /etc/dhcpcd.conf
systemctl restart dhcpcd

sed -i 's/^INTERFACESv4=.*/INTERFACESv4="ptusb0"/'  /etc/default/isc-dhcp-server
/usr/bin/pt-dhcp-server  stop
/usr/bin/pt-dhcp-server  start

sed -i 's/^net.ipv4.ip_forward=.*/#net.ipv4.ip_forward=0/' /etc/sysctl.conf
sh -c "echo 0 > /proc/sys/net/ipv4/ip_forward"
iptables -D FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -D FORWARD -i wlan0 -o eth0 -j ACCEPT
iptables -t nat -D  POSTROUTING -o eth0 -j MASQUERADE
