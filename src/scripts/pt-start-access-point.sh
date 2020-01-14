#!/bin/bash
if [ -n "$1" ] && [ -n "$2" ] ;then
	sed -i 's/^ssid=.*/ssid='"$1"'/' /home/pi/hostapd.conf
	sed -i 's/^wpa_passphrase=.*/wpa_passphrase='"$2"'/' /home/pi/hostapd.conf
fi
cp /home/pi/hostapd.conf  /etc/hostapd/hostapd.conf
sed -i 's/^#DAEMON_CONF=.*/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/'   /etc/default/hostapd
sed -i 's/^DAEMON_CONF=.*/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/'   /etc/default/hostapd

sed -i 's/^#nohook wpa_supplicant/nohook wpa_supplicant/'  /etc/dhcpcd.conf
sed -i 's/^#static ip_address=192.168.63.1\/24/static ip_address=192.168.63.1\/24/'  /etc/dhcpcd.conf
sed -i 's/^#interface wlan0/interface wlan0/'  /etc/dhcpcd.conf
systemctl  restart dhcpcd

systemctl unmask hostapd
systemctl start hostapd
systemctl enable hostapd

sed -i 's/^INTERFACESv4=.*/INTERFACESv4="ptusb0 wlan0"/'  /etc/default/isc-dhcp-server
/usr/bin/pt-dhcp-server  stop
/usr/bin/pt-dhcp-server  start

#ifconfig wlan0 192.168.63.1

sed -i 's/^#net.ipv4.ip_forward=.*/net.ipv4.ip_forward=1/' /etc/sysctl.conf
sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
sh -c "iptables-save > /etc/iptables.ipv4.nat"
