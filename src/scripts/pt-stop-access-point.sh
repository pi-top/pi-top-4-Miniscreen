sudo systemctl stop hostapd
sudo systemctl disable hostapd

sudo ifconfig wlan0 0.0.0.0
sudo sed -i 's/^nohook wpa_supplicant/#nohook wpa_supplicant/'  /etc/dhcpcd.conf
sudo sed -i 's/^static ip_address=192.168.63.1\/24/#static ip_address=192.168.63.1\/24/'  /etc/dhcpcd.conf
sudo sed -i 's/^interface wlan0/#interface wlan0/'  /etc/dhcpcd.conf
sudo systemctl restart dhcpcd

sudo sed -i 's/^INTERFACESv4=.*/INTERFACESv4="ptusb0"/'  /etc/default/isc-dhcp-server
sudo /usr/bin/pt-dhcp-server  stop
sudo /usr/bin/pt-dhcp-server  start

sudo sed -i 's/^net.ipv4.ip_forward=.*/#net.ipv4.ip_forward=0/' /etc/sysctl.conf
sudo sh -c "echo 0 > /proc/sys/net/ipv4/ip_forward"
sudo iptables -D FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -D FORWARD -i wlan0 -o eth0 -j ACCEPT
sudo iptables -t nat -D  POSTROUTING -o eth0 -j MASQUERADE

