#!/bin/bash
if [ -n "$1" ] && [ -n "$2" ] ;then
sudo sed -i 's/^ssid=.*/ssid='$1'/' /home/pi/hostapd.conf
sudo sed -i 's/^wpa_passphrase=.*/wpa_passphrase='$2'/' /home/pi/hostapd.conf
fi
sudo cp /home/pi/hostapd.conf  /etc/hostapd/hostapd.conf
sudo sed -i 's/^#DAEMON_CONF=.*/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/'   /etc/default/hostapd
sudo sed -i 's/^DAEMON_CONF=.*/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/'   /etc/default/hostapd

sudo sed -i 's/^#nohook wpa_supplicant/nohook wpa_supplicant/'  /etc/dhcpcd.conf
sudo sed -i 's/^#static ip_address=192.168.63.1\/24/static ip_address=192.168.63.1\/24/'  /etc/dhcpcd.conf
sudo sed -i 's/^#interface wlan0/interface wlan0/'  /etc/dhcpcd.conf
sudo systemctl  restart dhcpcd

sudo systemctl unmask hostapd
sudo systemctl start hostapd
sudo systemctl enable hostapd


sudo sed -i 's/^INTERFACESv4=.*/INTERFACESv4="ptusb0 wlan0"/'  /etc/default/isc-dhcp-server
sudo /usr/bin/pt-dhcp-server  stop
sudo /usr/bin/pt-dhcp-server  start

#sudo ifconfig wlan0 192.168.63.1

sudo sed -i 's/^#net.ipv4.ip_forward=.*/net.ipv4.ip_forward=1/' /etc/sysctl.conf
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
sudo iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT 
sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
