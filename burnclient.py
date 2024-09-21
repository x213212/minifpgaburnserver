#!/home/project/utils/bin/python3 
import requests
import json
import argparse
import socket

# burn bitmap
#python3 burnclient.py --burnserver 10.0.12.188:1234 --event run-vivado --icemanpath C:\\path\\to\\iceman.bat --vivadopath C:\\path\\to\\vivado_lab.bat --tclscript burnbit.tcl --icemancommand "-D -Z v5 -p 1236" --bitmappath "bitmaps\\generic\\generic_chip.bit"
# run iceman
#python3 burnclient.py --burnserver 10.0.12.188:1234 --event run-iceman --icemanpath C:\\path\\to\\iceman.bat --vivadopath C:\\path\\to\\vivado_lab.bat --tclscript burnbit.tcl --icemancommand "-D -Z v5 -p 1236" --bitmappath "bitmaps\\generic\\generic_chip.bit"
# list all thread id 
#python3 burnclient.py --burnserver 10.0.12.188:1234 --event list-threads --icemanpath C:\\path\\to\\iceman.bat --vivadopath C:\\path\\to\\vivado_lab.bat --tclscript burnbit.tcl --icemancommand "-D -Z v5 -p 1236" --bitmappath "bitmaps\\generic\\generic_chip.bit"
# kill thread id
#python3 burnclient.py --burnserver 10.0.12.188:1234 --event stop-thread --icemanpath C:\\path\\to\\iceman.bat --vivadopath C:\\path\\to\\vivado_lab.bat --tclscript burnbit.tcl --icemancommand "-D -Z v5 -p 1236" --bitmappath "bitmaps\\generic\\generic_chip.bit"
# get thread log 
#python3 burnclient.py --burnserver 10.0.12.188:1234 --event get-logs --icemanpath C:\\path\\to\\iceman.bat --vivadopath C:\\path\\to\\vivado_lab.bat --tclscript burnbit.tcl --icemancommand "-D -Z v5 -p 1236" --bitmappath "bitmaps\\generic\\generic_chip.bit"
# reset usb 
#python3 burnclient.py --burnserver 10.0.12.188:1234 --event reset-serial-ports --icemanpath C:\\path\\to\\iceman.bat --vivadopath C:\\path\\to\\vivado_lab.bat --tclscript burnbit.tcl --icemancommand "-D -Z v5 -p 1236" --bitmappath "bitmaps\\generic\\generic_chip.bit"

parser = argparse.ArgumentParser(description="Python script for parameter passing")

parser.add_argument('--burnserver', type=str, help="burnserver")
parser.add_argument('--event', type=str, help="event")
parser.add_argument('--vivadopath', type=str, help="vivado path")
parser.add_argument('--icemanpath', type=str, help="iceman path")
parser.add_argument('--tclscript', type=str, help="tcl script")
parser.add_argument('--icemancommand', type=str, help="tcl command")
parser.add_argument('--bitmappath', type=str, help="bitmappath")
args = parser.parse_args()

try:
    server_ip = socket.gethostbyname(args.burnserver.split(":")[0])+":"+args.burnserver.split(":")[1]
    print(f"Resolved {args.burnserver} to {server_ip}")
except socket.gaierror:
    print(f"Error: Unable to resolve host {server_ip}")
    exit(1)
# The server URL
burn_url = f"http://{server_ip}/{args.event}"
print(args.bitmappath)
# The TCL script path and any additional arguments (adjust as needed)
tcl_script_path = f"{args.tclscript}"  # Example: Path to your TCL script

vivado_path = rf"{args.vivadopath}"
iceman_path = rf"{args.icemanpath}"
iceman_command = rf"{args.icemancommand}"

# POST request with the tcl_script and additional args to be run
response = requests.post(burn_url, json={'burnserver': server_ip,'tcl_script': tcl_script_path,'vivado_script': vivado_path,'icemanpath': iceman_path, 'icemancommand' :iceman_command,'bitmappath':args.bitmappath})    
# Print the result
if response.status_code == 200:
    # print("API response")
    print(f"Response: {response.text}")
else:
    # print("API response error")
    print(f"Response: {response.text}")
