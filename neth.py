# ============================================================
# IMPORTS
# ============================================================
from getpass import getpass
from netmiko import ConnectHandler
from datetime import datetime
import argparse
import logging
from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
    ConfigInvalidException,
)

# ============================================================
# VARS AND DEFINITIONS
# ============================================================
success_counter: int = 0
fail_counter: int = 0
error_dict: dict[str, str] = {}

# ============================================================
# BANNER AND SUMMARY
# ============================================================
def banner():
	print(r"""\
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
""")
# the \ in print(r"""\ is used to escape the newline character 
# and print the banner without indentation on the commandline

def summary(success_counter: int, fail_counter: int, error_dict: dict[str, str]):
    print(f"""\
==============================
Execution Summary
==============================
Successful: {success_counter}
Failed: {fail_counter}

Failed devices:\
""")
    for device in error_dict:
        print(f"{error_dict[device]}")

# ============================================================
# CUSTOM EXCEPTIONS
# ============================================================
class FileEmptyError(Exception):
    """Raised when an input file is empty."""
    pass

# ============================================================
# OPEN FILES
# ============================================================
def open_commands(commands_file: str = "commands.txt") -> list[str]:
    with open(commands_file) as f:
        commands = [line.strip() for line in f if line.strip()]
        # line.strip() removes whitespace from the beginning and end of each line
        # if line.strip() filters out lines that are empty or contain only whitespace.
        # otherwise FileEmptyError wouldn't get raised because an empty character in the file
        # would prevent the raise

    if not commands:
        raise FileEmptyError(f"The commands file '{commands_file}' is empty.")
        # raise a custom exception if the commands file is empty
    return commands

def open_devices(devices_file: str = "devices.txt") -> list[str]:
    with open(devices_file) as f:
        devices = [line.strip() for line in f if line.strip()]
        # line.strip() removes whitespace from the beginning and end of each line
        # if line.strip() filters out lines that are empty or contain only whitespace.
        # otherwise FileEmptyError wouldn't get raised because an empty character in the file
        # would prevent the raise

        if not devices:
            raise FileEmptyError(f"The devices file '{devices_file}' is empty.")
            # raise a custom exception if the devices file is empty
    return devices

def write_output(output: str, device: str) -> None:
        with open(f"{device}_{datetime.now().strftime('%d%m%Y_%H%M')}.txt", "w") as logfile:
            logfile.write(output)
            # open the file output.txt, a file to redirect the output to 

# ============================================================
# LOGGING
# ============================================================
def configure_logging() -> None:
    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s - %(levelname)s - %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S",
    )

    logging.getLogger("paramiko").setLevel(logging.WARNING)
    # raise paramiko logging level to warning 
    # to reduce spam output in the console

# ============================================================
# COMMAND LINE PARSER
# ============================================================
def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=""
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
        help="Path to the file containing show or configuration commands (default: commands.txt)"
    )
    # same as above but for the commands file

    parser.add_argument(
        "-t", "--type",
        default="cisco_ios",
        help="Specify the vendor type (default: cisco_ios, example options: cisco_xe, cisco_asa, juniper_junos, arista_eos for more info see netmiko supported platforms)"
    )

    parser.add_argument(
        "-m", "--mode",
        default="show",
        choices=["show", "config"],
        help="Execute the commands from the file in privileged exec mode (show) or configuration mode (config) (default: show)"
    )
    # same as above but for the mode of execution, either show or config
    # you can use it like this script.py --mode show or script.py --mode config

    return parser.parse_args()

# ============================================================
# CREDENTIALS
# ============================================================
def credentials() -> tuple[str, str]:
    username: str = input('Enter your SSH username: ')
    password: str = getpass()
    return username, password

# ============================================================
# PROCESS DEVICE AND ERROR HANDLING
# ============================================================
def process_device(device: str, commands: list[str], credentials: tuple[str, str], mode: str, type: str, error_dict: dict[str, str]) -> bool:
    try:
        logging.info(f"Trying to connect to {device} ...")

        device_config = {
            "device_type": type,
            "ip": device,
            "username": credentials[0],
            "password": credentials[1],
            "timeout": 10,
            # general socket timeout used by the underlying connection
            "conn_timeout": 10
            # controls how long netmiko waits while establishing the SSH connection
        }
        # iterate over the devices e.g. IPs from args.devices file 
        # and store the data in a dictionary to connect to the device 
        # via netmiko ConnectHandler in the next step

        net_connect = ConnectHandler(**device_config)
        # create the connection to the device using the data from the dictionary ios_device
        logging.info(f"Connection established to {net_connect.find_prompt()}")
        # prints the prompt of the current device e.g. ASW1#

        output = ""
        if mode == "show":
            # if the user specified show mode via script.py --mode show, 
            # execute the commands in privileged exec mode aka enable mode
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
                    read_timeout=60
                    # controls how long send_command() waits for the command to execute
                )
                # send the command to the device and store the output in the variable output
                # iterate over the commands in the commands.txt file until all commands have been executed
                output += "\n\n\n"
                # create some space between the output of the commands to make it more readable

        elif mode == "config":
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

        write_output(output, device)

        '''
        with open(f"{device}_{datetime.now().strftime('%d%m%Y_%H%M')}.txt", "w") as logfile:
            logfile.write(output)
        net_connect.disconnect()
        # the output of the commands is stored in a variable named output
        # write the output of the commands from commands.txt to a file named IP + timestamp + .txt
        '''

        logging.info(f"Completed execution on {device}\n")
        # disconnect and move on to the next iteration of the for loop 
        # to execute the same steps on the next device

        return True

    except NetmikoAuthenticationException as e:
        logging.error(f"[AUTH ERROR] {device}: Authentication failed - {e}")
        error_dict[device] = f"[AUTH ERROR] {device} : Authentication failed"

    except NetmikoTimeoutException as e:
        logging.error(f"[TIMEOUT] {device}: Connection timed out - {e}")
        error_dict[device] = f"[TIMEOUT] {device}: Connection timed out"

    except ConfigInvalidException as e:
        logging.error(f"[CONFIG ERROR] {device}: Invalid configuration command - {e}")
        error_dict[device] = f"[CONFIG ERROR] {device}: Invalid configuration command"

    except FileNotFoundError as e:
        logging.error(f"[FILE ERROR] {device}: File not found - {e}")
        error_dict[device] = f"[FILE ERROR] {device}: File not found"

    except PermissionError as e:
        logging.error(f"[PERMISSION ERROR] {device}: Permission denied - {e}")
        error_dict[device] = f"[PERMISSION ERROR] {device}: Permission denied"

    except EOFError as e:
        logging.error(f"[EOF ERROR] {device}: Unexpected end of input - {e}")
        error_dict[device] = f"[EOF ERROR] {device}: Unexpected end of input"
    except OSError as e:
        logging.error(f"[OS ERROR] {device}: {e}")
        error_dict[device] = f"[OS ERROR] {device}: {e}"

    except Exception as e:
        logging.error(f"[ERROR] {device}: {type(e).__name__} - {e}")
        error_dict[device] = f"[ERROR] {device}: {type(e).__name__} - {e}"
    return False

# ============================================================
# MAIN
# ============================================================ 
def main(success_counter: int = success_counter, fail_counter: int = fail_counter):
    try:
        banner()
        # call the banner function to print the banner at the start of the script

        configure_logging()

        args: argparse.Namespace = parse_arguments()
        # reads the command-line arguments that the user passed to the script, 
        # validates them and stores the results in an object
        # afterwards you can use the provided arguments 
        # e.g. you can use the provided file which holds the commands like this: args.commands
        # or the file that holds the devices like this: args.devices

        commands: list[str] = open_commands(args.commands)

        get_credentials:tuple[str, str] = credentials()
        # credentials() returns a tuple 
        # with element[0] = username and element[1] = password

        for device in open_devices(args.devices):
            if process_device(device, commands, get_credentials, args.mode, args.type, error_dict):
            # call the process_device function to connect to the device and execute the commands
            # pass the device IP, commands list, credentials tuple and args.mode to the function
                success_counter += 1
            else:
                fail_counter += 1

        #print(f"success_counter is: {success_counter}")

    except KeyboardInterrupt:
        logging.info("\n[INFO] Script interrupted by user.")

    except FileNotFoundError as e:
        logging.error(f"[FILE ERROR] File not found: {e}")

    except PermissionError as e:
        logging.error(f"[PERMISSION ERROR] Permission denied: {e}")

    except FileEmptyError as e:
        logging.error(f"[FILE EMPTY ERROR] Empty file: {e}")

    summary(success_counter, fail_counter, error_dict)

if __name__ == "__main__":
    main()