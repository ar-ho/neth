# ============================================================
# IMPORTS
# ============================================================
from getpass import getpass
from netmiko import ConnectHandler
import argparse
import logging
from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
    ConfigInvalidException,
)

# ============================================================
# FUNCTIONS
# ============================================================
def open_commands(commands_file: str = "commands.txt") -> list[str]:
    with open(commands_file) as f:
        return f.read().splitlines()
# open the file commands.txt which contains the commands to execute

def open_devices(devices_file: str = "devices.txt") -> list[str]:
    with open(devices_file) as f:
        return f.read().splitlines()
# open the file devices.txt which contains the IP address of the devices to connect to
 
def open_output(output_file: str = "output.txt") -> list[str]:
    with open(output_file) as f:
        return f.read().splitlines()
# open the file output.txt, a file to redirect the output to 

def banner():
    print(r"""

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
    """
    )

banner()
# call the banner function to print the banner at the start of the script
# see functions section for more info

# ============================================================
# COMMAND LINE PARSER
# ============================================================
parser = argparse.ArgumentParser(
    description="Connect to Cisco IOS devices using Netmiko and execute commands."
)
# argparse is the module used to create the help output when using python <script-name> --help
# argparse.ArgumentParser is the class used to create the argument parser
# the instance is saved in parser

parser.add_argument(
    "-d", "--devices",
    default="devices.txt",
    help="Path to the file containing device IP addresses (default: devices.txt)"
)
# parser.add_argument creates an option for python3 <script-name> --devices or -d 
# to specify a file containing device IP addresses
# the default is devices.txt

parser.add_argument(
    "-c", "--commands",
    default="commands.txt",
    help="Path to the file containing configuration commands (default: commands.txt)"
)
# same as above but for the commands file

parser.add_argument(
    "-m", "--mode",
    default="show",
    choices=["show", "config"],
    help="Execute the commands from the file in privileged exec mode (show) or configuration mode (config) (default: show)"
)
# same as above but for the mode of execution, either show or config
# you can use it like this script.py --mode show or script.py --mode config

args = parser.parse_args()
# reads the command-line arguments that the user passed to the script, 
# validates them, and stores the results in an object
# afterwards you can use the provided arguments 
# e.g. you can use the provided file which holds the commands like this: args.commands
# or the file that holds the devices like this: args.devices

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(levelname)s - %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
)

logging.getLogger("paramiko").setLevel(logging.WARNING)
# raise paramiko logging level to warning to reduce spammy output in the console

# ============================================================
# CREDENTIALS
# ============================================================
username: str = input('Enter your SSH username: ')
password: str = getpass()
# get credentials from the user for the devices to connect to
# not done via command line arguments for security reasons

# ============================================================
# LOAD COMMANDS AN PROCESSING LOOP
# ============================================================
commands = open_commands(args.commands)
# places the file provided by the user which is specified via args.commands via commandline arguments in open_commands()
# the default for args.commands is commands.txt

for device in open_devices(args.devices):
    logging.info(f"Connecting to {device}")
    ios_device = {
        'device_type': 'cisco_ios',
        'ip': device,
        'username': username,
        'password': password
    }
# iterate over the devices e.g. IPs from args.devices file 
# and store the data in a dictionary to connect to the device via netmiko

# ============================================================
# EXECUTE COMMANDS ON DEVICES
# ============================================================
    try:
        net_connect = ConnectHandler(**ios_device)
        # create the connection to the device using the data from the dictionary ios_device
        logging.info(f"Connection established to {net_connect.find_prompt()}")
        # prints the prompt of the current device e.g. ASW1#

        output = ""
        if args.mode == "show":
            # if the user specified show mode via script.py --mode show, execute the commands in privileged exec mode
            for command in commands:
                # read in a line i.e. a command from the commands.txt file and store it in the variable command
                #output += f"\n{'=' * 60}\n"
                # this is a separator line to make the output more readable, commented out
                output += f"{command}\n"
                #adds the command to the output variable so that it is printed in the output file
                #output += f"{'=' * 60}\n"
                # this is a separator line to make the output more readable, commented out
                logging.info(f"Trying to execute {command}")
                output += net_connect.send_command(
                    command,
                    read_timeout=60,
                )
                # send the command to the device and store the output in the variable output
                # iterate over the commands in the commands.txt file until all commands have been executed
                output += "\n\n\n"
                # create some space between the output of the commands to make it more readable

        elif args.mode == "config":
            # if the user specified config mode via script.py --mode config, execute the commands in configuration mode
            output = net_connect.send_config_set(commands)
            # we can provide the commands file directly to send_config_set()
            # with show commands send_command() we need to iterate over the commands in the file as done previously in the show mode section
            # save the output of the commands from commands.txt to a variable output

        # why do we need to differentiate between show and config commands?
        # show running-config and other show commands do not work with send_config_set()
        # it only shows the first 10 lines of the running-config
        # we have to use send_command() for show commands and send _config_set() for config commands
        # send_command() cannot directly execute commands from a file, 
        # so we have to iterate over the commands in the file 

        with open(f"{device}.txt", "w") as logfile:
            logfile.write(output)
        net_connect.disconnect()
        # the output of the commands is stored in a variable named output
        # write the output of the commands from commands.txt to a file named IP + .txt

        logging.info(f"Completed execution on {device}\n")
        # disconnect and move on to the next iteration of the for loop 
        # to execute the same steps on the next device

# ============================================================
# ERROR HANDLING
# ============================================================
    except NetmikoAuthenticationException as e:
        logging.error(f"[AUTH ERROR] {device}: Authentication failed - {e}")

    except NetmikoTimeoutException as e:
        logging.error(f"[TIMEOUT] {device}: Connection timed out - {e}")

    except ConfigInvalidException as e:
        logging.error(f"[CONFIG ERROR] {device}: Invalid configuration command - {e}")

    except FileNotFoundError as e:
        logging.error(f"[FILE ERROR] {device}: File not found - {e}")

    except PermissionError as e:
        logging.error(f"[PERMISSION ERROR] {device}: Permission denied - {e}")

    except EOFError as e:
        logging.error(f"[EOF ERROR] {device}: Unexpected end of input - {e}")

    except KeyboardInterrupt:
        logging.info("\n[INFO] Script interrupted by user.")
        break

    except OSError as e:
        logging.error(f"[OS ERROR] {device}: {e}")

    except Exception as e:
        logging.error(f"[ERROR] {device}: {type(e).__name__} - {e}")