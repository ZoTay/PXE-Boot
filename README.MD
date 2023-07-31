#  RPI install and basic set-up
The setup uses Raspberry Pi OS Lite (Headless Mode). 
## Manual Setup
1. Install Raspberry Pi OS Lite to a available micro sd card (8GB minimum)
2. It is recommended to log in through SSH so you can copy paste some stuff
3. Install dnsmasq, apache and pxelinux
```
sudo apt-get update && sudo apt-get install dnsmasq pxelinux apache2
```
4. Create directory for netboot and TFTP files
```
sudo mkdir -p /mnt/data/netboot/bios
```
5. Create directory for hosting kernel and initial ramdisk files
```
sudo mkdir -p /mnt/data/netboot/boot/amd64/debian/12
```

6. Download and copy over netboot files
```
wget https://deb.debian.org/debian/dists/bookworm/main/installer-amd64/current/images/netboot/netboot.tar.gz
tar -xf netboot.tar.gz 
sudo cp debian-installer/amd64/{initrd.gz,linux} /mnt/data/netboot/boot/amd64/debian/12
sudo mv /mnt/data/netboot/boot/amd64/debian/12/linux /mnt/data/netboot/boot/amd64/debian/12/vmlinuz
```
7. Copy the files required for PXE 
```
sudo cp /usr/lib/syslinux/modules/bios/{ldlinux,vesamenu,libcom32,libutil}.c32  /usr/lib/PXELINUX/pxelinux.0 /mnt/data/netboot/bios
```
8. Attach a static IP address to the ethernet port
```
echo -e "interface eth0\nstatic ip_address=192.168.0.10/24" | sudo tee -a /etc/dhcpcd.conf
sudo systemctl restart dhcpcd
```
9. Configure /etc/dnsmasq.conf to enable the DHCP, PXE and TFTP and configure the 3 services

```echo -e "interface=eth0\nlisten-address=::1,127.0.0.1,192.168.0.10\ndhcp-range=192.168.0.11,192.168.0.255, 12h\nenable-tftp\ntftp-root=/mnt/data/netboot\npxe-service=x86PC,\"PXELINUX (BIOS)\",bios/pxelinux\nlog-queries\nlog-facility=/var/log/dnsmasq.log" | sudo tee -a /etc/dnsmasq.conf
sudo systemctl restart dnsmasq
```
10. Create directory for pxelinux config file
```
sudo mkdir -p /mnt/data/netboot/pxelinux.cfg
```
11. Create configuration file “default”, if you want to create a configuration file for a specific mac address, use in the format 01-XX-XX-XX-XX-XX-XX and replace XX with the mac address. 01 means that the connection is through an ethernet port. Refer to https://wiki.syslinux.org/wiki/index.php?title=PXELINUX for more details
```
sudo nano /mnt/data/netboot/pxelinux.cfg/default
Copy text over from **PXE-Boot-main/rpi/mnt/data/netboot/pxelinux.cfg**
```
12. Create directory for Apache server usage
```
sudo mkdir -p /var/www/deb
```
13. Set-up Apache Server
```
sudo nano /etc/apache2/sites-available/debian.conf
Copy text over from **PXE-Boot-main/rpi/etc/apache2/sites-available/debian.conf**
sudo a2ensite /etc/apache2/sites-available/debian.conf
sudo a2dissite /etc/apache2/sites-available/000-default.conf
sudo systemctl restart apache2
```
14. Set up preseed.cfg file for server to grab during set-up. 

- You can skip the part after and including “d-i preseed/late_command string” as they are used for setting up the challenges. 
If you are planning on doing an online install, change “d-i mirror/http/hostname” to an online repo instead of the RPI itself
```
sudo nano /var/www/deb/preseed.cfg
Copy over text from **PXE-Boot-main/rpi/var/www/deb/preseed.cfg**
```
15. Offline Install (Optional)
- Manual
    - Pipe internet connection through the computer
    - Use wireshark to sniff the packages downloaded and installed during online installation
    - Export logs from wireshark
    - Use the python script **PXE-Boot-main/debian dep downloader.py** to download and put the files in the correct directory and copy the var folder to the root directory of the RPI

- Preset
    - Download the debian folder PXE-Boot-main/rpi/var/www/deb and copy it to /var/www/deb folder

16. Restart RPI
```
sudo reboot now
```
17.  Challenges setup (Optional)
```
sudo nano /var/www/deb/motd
Copy over text from PXE-Boot-main/rpi/var/www/deb/motd 
sudo nano /var/www/deb/index.html
Copy over text from PXE-Boot-main/rpi/var/www/deb/index.html
sudo mkdir -p /var/www/dns
sudo nano /var/www/dns/index.html
Copy over text from PXE-Boot-main/rpi/var/www/ddns/index.html 
sudo nano /etc/apache2/sites-available/dns.conf
Copy over text from PXE-Boot-main/rpi/etc/apache2/sites-available/dns.conf
sudo a2ensite /etc/apache2/sites-available/dns.conf
sudo systemctl restart apache2
```
## Automatic Setup
Flash .img file to an empty micro sd card

Boot into system with username: radio and Password: googleswag

# OS Configuration
All configurations are done through the preseed.cfg file with the line 
d-i preseed/late_command string

The OS files are located in the /target directory
For any commands to be used from the OS, use the in-target prefix before the command, skip using /target and use / as it will be run in the /target directory
If you are piping to a file using echo, do not use the in-target prefix as it ignores the piping and be piped to stdout instead and not to the targeted file
