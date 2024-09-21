# FPGA Burn Server and Client

This project provides Python scripts to automate FPGA programming tasks, including bitmap burning, thread management, log retrieval, and USB serial port resetting, using tools like [Andestech's ICEman](https://github.com/andestech/ICEman) and Xilinx Vivado Lab. The server (`burnserver.py`) processes requests through a Flask-based API, while the client (`burnclient.py`) sends commands to initiate tasks on the server.

## Features Overview
### 1.Example Server Start (With Administrator Privileges)
Key Server API Endpoints:
/run-vivado: Executes Vivado scripts to program the FPGA with a bitmap file.
/run-iceman: Executes ICEman commands to manage FPGA programming tasks.
/list-threads: Lists all active threads running on the server.
/stop-thread: Terminates a specific thread based on command options.
/get-logs: Retrieves execution logs for FPGA programming tasks.
/reset-serial-ports: Resets USB serial ports by disabling and re-enabling them, simulating a replugging action.
To start the server with administrator privileges:
Linux/macOS: Use sudo

```bash
sudo python3 burnserver.py
```
Windows: Run the terminal as Administrator and execute:
```bash
python3 burnserver.py
```
The server will listen for requests on 0.0.0.0:1234 by default.

### 2.FPGA Bitmap Burning (`burnclient.py`)
The `burnclient.py` script offers a command-line interface for sending requests to the burn server. Users can specify paths to Vivado and ICEman executables, TCL scripts, and FPGA bitmap files to automate the programming process.

#### Example Usage
```bash
# Send a request to burn a bitmap using burnclient.py
python3 burnclient.py --burnserver 10.0.12.188:1234 --event run-vivado --icemanpath C:\\path\\to\\iceman.bat --vivadopath C:\\path\\to\\vivado_lab.bat --tclscript burnbit.tcl --icemancommand "-D -Z v5 -p 1236" --bitmappath "bitmaps\\generic\\generic_fpga.bit"
```



