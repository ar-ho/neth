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


# Neth - NetHelper
Neth is a commandline tool made for configuring and managing multiple network devices like switches and routers at the same time. All you need is Python and Netmiko installed on your machine and SSH access to the network devices.

Instead of tediously logging in to each device manually, just put your commands and device IPs in a file, run Neth and it will connect to each device, run the commands and save the output automaically.

Neth supports both show and configuration commands, error handling, logging, per device output files and more. Making it a great tool for network configuration, administration and troubleshooting.

![Gameplay](gameplay.gif) 

## 🏆 Motivation


Building a game like this is a great way to develop programming skills because it provides immediate visual feedback. Every change in the code can be directly seen in the behavior of the game.  
Working on a game project also offers practical experience with problem-solving, game logic, collision detection, user input, and graphical rendering. Progress is visible from the beginning which helps to maintain motivation.

## 💬 Disclaimer:
This is a project that started out from boot.dev - I recommend to check them out!  
The source code is not entirely written by me.    
Especially the math was done for me by boot.dev.  
I added and will add more features myself as time goes on. 

## 🚀 Quick Start
### Linux
1. Install Git and Python3 via the commandline.

2. Create and navigate to the directory where you want to store the repo:
```
mkdir ~/projects
cd ~/projects
```

3. Clone the repository:
```
git clone https://github.com/ar-ho/astroblast.git
```

4. Execute main.py.
```
python3 ~/projects/astroblast/main.py
```

### Windows
1. Install Git and Python3.

2. Add Git and Python3 to your PATH environment variable.

3. Clone the repo using the Git bash cli for windows.

4. Execute main.py

## 📖 Usage
- Use WASD keys to move and space for shooting.

## 🤝 Contributing
Feel free to clone, use and enhance this code.
### Submit a pull request
If you would like to contribute, please fork the repository and open a pull request to the `main` branch.

### INSTALLATION on the ubuntu box in GNS3
apt update
apt upgrade -y
apt install python3 -y
apt install python3-pip -y
pip install telnetlib3 --break-system-packages
pip install -U netmiko --break-system-packages

### TO DO
Your script is already at a good level for a personal network automation tool. The next improvements are less about "making it work" and more about making it maintainable, safer, and closer to production-quality automation.

Here are the improvements I would prioritize:

1. Use the logging module instead of print() (high priority)

Right now:

print(f"Connecting to {device}")

works, but professional automation scripts usually use logging because you can:

add timestamps,
write to a log file,
control verbosity,
separate info/warning/error messages.

Example:

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logging.info(f"Connecting to {device}")

Output:

2026-08-05 20:10:12 [INFO] Connecting to 192.168.1.10

For troubleshooting network changes, logs are much more useful than terminal output.

2. Add a main() function (high priority)

Currently your script executes immediately when Python imports it.

Professional Python scripts usually have:

def main():
    # script logic here


if __name__ == "__main__":
    main()

Benefits:

easier testing,
reusable functions,
cleaner structure,
prevents accidental execution when imported.

Your structure would become:

imports

functions

main()

if __name__ == "__main__":
    main()
3. Add a device_type argument

Currently:

'device_type': 'cisco_ios'

is hardcoded.

If you later work with:

Cisco NX-OS
Cisco ASA
Arista EOS
Juniper Junos

you need to edit the script.

Better:

parser.add_argument(
    "--platform",
    default="cisco_ios",
    help="Netmiko device type"
)

Then:

'device_type': args.platform

Example:

python script.py --platform cisco_nxos
4. Validate your input files

Currently:

with open(commands_file) as f:

will fail if:

the file does not exist,
it is empty,
it contains blank lines.

A more robust function:

def open_commands(commands_file):
    with open(commands_file) as f:
        return [
            line.strip()
            for line in f
            if line.strip()
        ]

This removes empty commands.

5. Add connection parameters

Netmiko has useful options you are not using:

ios_device = {
    "device_type": "cisco_ios",
    "ip": device,
    "username": username,
    "password": password,
    "timeout": 10,
    "conn_timeout": 10,
}

Benefits:

avoids hanging forever,
easier troubleshooting.
6. Use with ConnectHandler() if possible

Instead of:

net_connect = ConnectHandler(**ios_device)

...

net_connect.disconnect()

You can use:

with ConnectHandler(**ios_device) as net_connect:
    output = net_connect.send_command(command)

The connection automatically closes even if something fails.

7. Add timestamps to output files

Currently:

192.168.1.10.txt

gets overwritten every time.

Better:

192.168.1.10_2026-08-05_201500.txt

Example:

from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

filename = f"{device}_{timestamp}.txt"

Very useful when you collect backups or troubleshooting outputs.

8. Add connection success/failure summary

For multiple switches, something like:

==============================
Execution Summary
==============================
Successful: 18
Failed: 2

Failed devices:
- 10.1.1.20 Authentication failed
- 10.1.1.30 Timeout

is much more professional than scrolling through output.

9. Add send_command() error handling per command

Currently one failed command stops the whole device.

Example:

for command in commands:
    try:
        output += net_connect.send_command(command)
    except Exception as e:
        output += f"{command} failed: {e}"

If:

show ip route

fails, you still collect:

show version
show interfaces
10. Add type hints everywhere

You already started doing this:

def open_commands(commands_file: str = "commands.txt") -> list[str]:

Good practice.

Extend it:

from netmiko import BaseConnection

def execute_commands(
    connection: BaseConnection,
    commands: list[str]
) -> str:

Makes larger projects easier to maintain.

11. Remove unused code

You have:

def open_output(output_file: str = "output.txt") -> list[str]:

but it is never used.

Professional scripts should avoid unused functions unless they are planned features.

12. Add a README if this is a GitHub project

A good network automation repository usually includes:

README.md
requirements.txt
script.py
devices.txt.example
commands.txt.example

The README should explain:

installation,
usage,
examples,
supported platforms.
If I were reviewing this as a network automation project, my priority order would be:
Priority	Improvement
⭐⭐⭐⭐⭐	Add main()
⭐⭐⭐⭐⭐	Replace print() with logging
⭐⭐⭐⭐⭐	Improve exception handling
⭐⭐⭐⭐	Add timestamps to output
⭐⭐⭐⭐	Add command-level error handling
⭐⭐⭐	Add platform argument
⭐⭐⭐	Add config file support
⭐⭐	Add SSH key support

Your current script is already beyond a beginner script. The biggest jump in professionalism would come from better structure (main()), logging, and cleaner error handling, not from adding more comments or more features.
