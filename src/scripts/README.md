 

### Need install hostapd first:

    sudo apt-get install  hostapd

### need change the location hostapd.service file, otherwise after reboot hostapd don't work in AP mode  

    sudo mv /etc/systemd/system/multi-user.target.wants/hostapd.service  /etc/systemd/system/
    
    
     
### hostapd.conf and pt-start-access-point.sh, pt-stop-access-point.sh need be placed under /home/pi/
 
### /etc/dhcpcd.conf and /etc/dhcp/dhcpd.conf need be replaced by the corresponding files in this directory 

 

