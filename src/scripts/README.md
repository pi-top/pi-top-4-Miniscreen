 

### Need install hostapd first:

    sudo apt-get install  hostapd

### need change the location hostapd.service file, otherwise after reboot hostapd don't work in AP mode  

    sudo mv /etc/systemd/system/multi-user.target.wants/hostapd.service  /etc/systemd/system/
    
    
     

 


 


