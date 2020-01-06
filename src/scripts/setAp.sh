#!/bin/bash
if [ -n "$1" ] && [ -n "$2" ] ;then
sudo sed -i 's/^ssid=.*/ssid='$1'/' /home/pi/hostapd.conf
sudo sed -i 's/^wpa_passphrase=.*/wpa_passphrase='$2'/' /home/pi/hostapd.conf
fi
sudo cp /home/pi/hostapd.conf  /etc/hostapd/hostapd.conf
sudo sed -i 's/^#DAEMON_CONF=.*/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/'   /etc/default/hostapd
sudo sed -i 's/^DAEMON_CONF=.*/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/'   /etc/default/hostapd

sudo sed -i "/^network/,/^}$/d"  /etc/wpa_supplicant/wpa_supplicant.conf
sudo systemctl  restart dhcpcd

sudo systemctl unmask hostapd
sudo systemctl stop hostapd
sudo systemctl start hostapd

sudo sed -i 's/^INTERFACESv4=.*/INTERFACESv4="ptusb0 wlan0"/'  /etc/default/isc-dhcp-server
sudo /usr/bin/pt-dhcp-server  stop
sudo /usr/bin/pt-dhcp-server  start

sudo ifconfig wlan0 192.168.64.1
sudo ifconfig ptusb0 0.0.0.0

sudo sed -i 's/^#net.ipv4.ip_forward=.*/net.ipv4.ip_forward=1/' /etc/sysctl.conf
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
sudo iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
