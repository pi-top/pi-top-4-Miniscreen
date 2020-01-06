sudo systemctl stop hostapd
sudo sed -i 's/^INTERFACESv4=.*/INTERFACESv4="ptusb0"/'  /etc/default/isc-dhcp-server
sudo ifconfig wlan0 0.0.0.0
sudo ifconfig ptusb0 192.168.64.1
sudo /usr/bin/pt-dhcp-server  stop
sudo /usr/bin/pt-dhcp-server  start
sudo sed -i 's/^net.ipv4.ip_forward=.*/#net.ipv4.ip_forward=0/' /etc/sysctl.conf
sudo sh -c "echo 0 > /proc/sys/net/ipv4/ip_forward"
sudo iptables -t nat -D  POSTROUTING -o eth0 -j MASQUERADE
