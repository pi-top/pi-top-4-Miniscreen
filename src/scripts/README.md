 

### Install hostapd first:

    sudo apt-get install  hostapd

### Change the location hostapd.service file, otherwise after reboot hostapd don't work in AP mode  

    sudo mv /etc/systemd/system/multi-user.target.wants/hostapd.service  /etc/systemd/system/
    
    



 

### These threee files should be placed under /home/pi/
    hostapd.conf and pt-start-access-point.sh, pt-stop-access-point.sh
 
 
 


### These two files should be replaced by the corresponding files in this directory 

    /etc/dhcpcd.conf and /etc/dhcp/dhcpd.conf


