```
#    # ###### ##### #    # 
##   # #        #   #    # 
# #  # #####    #   ###### 
#  # # #        #   #    # 
#   ## #        #   #    # 
#    # ######   #   #    # 

Neth - NetHelper
Network Configuration Tool
Multi Vendor | Netmiko | SSH

neth -h for instructions
```

# Neth - NetHelper
Neth is a commandline tool made for configuring and managing multiple network devices like switches and routers at the same time. All you need is Python and Netmiko installed on your machine and SSH access to the network devices.

Instead of tediously logging in to each device manually, just put your commands and device IPs in a file, run Neth and it will connect to each device, run the commands and save the output automatically.

Neth supports both show and configuration commands, error handling, logging, per device output files and more. Making it a great tool for network configuration, administration and troubleshooting.

## Disclaimer
This script is provided "as is". Use at your own risk! 
The author is not responsible for any damage, configuration changes, downtime, data loss or other issues resulting from its use. 
Always test the script in a non-production first!

## 🏆 Motivation
The motivation behind this script is to provide an easy to use, powerful script that runs anywhere with minimal overhead and a small number of requirements. 
The main goals I wanted to achieve were the following: 
- Multi device support to save time on manual and repetitive configuration tasks.
- Multi vendor support.
- Platform independence.
- Easy to use.

This script can be used by non technical people easily.
Which makes it useful for many everyday network-related tasks. 
For example, sales employees could use it to check the software version accross multiple devices, while support engineers could configure a new user on all devices in a network without having to log in to each device manually.

## 🚀 Quick Start
### Linux (Debian/Ubuntu)
Install Python 3, Pip and Git if they are not already installed.
Open your terminal e.g bash and run:

```
sudo apt update
sudo apt upgrade -y
sudo apt install python3 -y python3-pip git -y
pip install -U netmiko
git clone https://github.com/ar-ho/neth ~/neth
python3 ~/neth/neth.py --help
```

After cloning the repository run ```neth.py --help``` to display the available options.

### Windows
Install Python 3, Pip and Git if they are not already installed.
Open PowerShell and run:

```
git clone https://github.com/ar-ho/neth.git "$HOME\neth"
cd "$HOME\neth"
python -m pip install -U netmiko
python .\neth.py --help
```

After cloning the repository run ```neth.py --help``` to display the available options.

## 📖 Usage
```
usage: neth.py [-h] [-d DEVICES] [-c COMMANDS] [-t TYPE] [-m {show,config}]

options:
  -h, --help            show this help message and exit
  -d, --devices DEVICES
                        Path to the file containing device IP addresses (default: devices.txt)
  -c, --commands COMMANDS
                        Path to the file containing show or configuration commands (default: commands.txt)
  -t, --type TYPE       Specify the vendor type (default: cisco_ios, example options: cisco_xe, cisco_asa,
                        juniper_junos, arista_eos for more info see netmiko supported platforms)
  -m, --mode {show,config}
                        Execute the commands from the file in privileged exec mode (show) or configuration mode
                        (config) (default: show)                 
```
### commands.txt examples
All commands below were executed on Cisco IOS and Cisco IOS-XE devices.

The following show commands would print the output of "show version | i Version" and "show vlan brief" into the output files for the devices:
```
root@UbuntuBox:~# cat commands.txt 
show version | i Version

show vlan brief
```

The next command "show running-config" would generate an output file containing the complete running configuration of each device i.e. a backup of each device’s configuration would be created.
```
root@UbuntuBox:~# cat commands.txt 
show running-config
```

Here is an example of a configuration task which creates vlan 2 and then configures vlan 2 on an interface, adds a description and finally brings the interface up:
```
root@UbuntuBox:~# cat commands.txt 
vlan 2
interface Ethernet0/0
description HelloWorld
switchport access vlan 2
no shutdown
```

### devices.txt example
```
root@UbuntuBox:~# cat devices.txt 
192.168.122.100
192.168.122.101
192.168.122.102
192.168.122.103
192.168.122.104
```

### example runs
Runs show commands: 
```root@UbuntuBox:~# python3 neth.py --mode show```
Runs config commands: 
```root@UbuntuBox:~# python3 neth.py --mode config```
Runs show commands from a custom commands file 
```root@UbuntuBox:~# python3 neth.py -c /home/anon/Downloads/mycommands.md```

## 🤝 Contributing
Feel free to clone, use and enhance this code.
### Submit a pull request
If you would like to contribute, please fork the repository and open a pull request to the `main` branch.