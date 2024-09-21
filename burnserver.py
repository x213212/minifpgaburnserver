from flask import Flask, request, jsonify
import subprocess
import os
import time
import threading
app = Flask(__name__)
threads = {}
logs = {}
processes = {}

@app.route('/run-vivado', methods=['POST'])
def run_vivado():
    try:
        # Get the necessary parameters from the request
        data = request.get_json()
        tcl_script = data.get('tcl_script', '')  # Path to the TCL script
        vivado_script = data.get('vivado_script', '')  # Path to the Vivado executable
        bitmap_path = data.get('bitmappath', '')  # Bitmap path to replace
        print(bitmap_path)
        # Check if all required parameters are provided
        if not tcl_script or not vivado_script or not bitmap_path:
            return jsonify({'error': 'Vivado script, TCL script, and bitmap path are required'}), 400

        # Ensure the paths exist
        if not os.path.exists(vivado_script):
            return jsonify({'error': f'Vivado script not found: {vivado_script}'}), 404

        if not os.path.exists(tcl_script):
            return jsonify({'error': f'TCL script not found: {tcl_script}'}), 404

        # Read the TCL script and replace BOARD_BITMAP_PATH with the actual bitmap_path
        with open(tcl_script, 'r') as file:
            tcl_content = file.read()

        # Replace the placeholder with the actual bitmap path
        updated_tcl_content = tcl_content.replace('BOARD_BITMAP_PATH', bitmap_path)

        # Write the updated script to a temporary file
        temp_tcl_script = 'updated_script.tcl'
        with open(temp_tcl_script, 'w') as file:
            file.write(updated_tcl_content)

        # Construct the command: vivado_lab.bat -mode tcl -source <TCL script>
        command = [vivado_script, '-mode', 'tcl', '-source', temp_tcl_script]
        print(f"Running command: {' '.join(command)}")

        # Run the command and capture output
        result = subprocess.run(command, capture_output=True, text=True, shell=True)

        # Clean up the temporary file after execution
        os.remove(temp_tcl_script)

        # Return the result of execution
        if result.returncode == 0:
            return jsonify({
                'status': 'success',
                'message': 'TCL script executed successfully',
                'stdout': result.stdout
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'TCL script execution failed',
                'stderr': result.stderr,
                'stdout': result.stdout
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_iceman_process(iceman_path, command_options, combin_output_name):
    try:

        bat_dir = os.path.dirname(iceman_path)
        home_dir = bat_dir

        cygpath = os.path.abspath(os.path.join(home_dir, ".."))

        os.environ['HOME'] = home_dir
        os.environ['CYGPATH'] = cygpath
        os.environ['PATH'] = f"{os.path.join(cygpath, 'cygwin', 'bin')};{home_dir};{os.environ['PATH']}"

        bash_path = os.path.join(cygpath, "cygwin", "bin", "bash.exe")
        if os.path.exists(bash_path):
            os.environ['SHELL'] = '/bin/bash'

        mintty_path = os.path.join(cygpath, "cygwin", "bin", "mintty.exe")
        command = [mintty_path, "/bin/bash", "-c", f'./ICEman.exe {command_options} | tee {combin_output_name}.log 2>&1']

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd=home_dir,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        processes[combin_output_name] = process  

        stdout_lines = []
        stderr_lines = []

        for stdout_line in iter(process.stdout.readline, ''):
            stdout_lines.append(stdout_line.strip())

        for stderr_line in iter(process.stderr.readline, ''):
            stderr_lines.append(stderr_line.strip())

        process.stdout.close()
        process.stderr.close()
        process.wait()

        return {'stdout': '\n'.join(stdout_lines), 'stderr': '\n'.join(stderr_lines), 'returncode': process.returncode}

    except Exception as e:
        return {'error': str(e)}

@app.route('/run-iceman', methods=['POST'])
def run_iceman():
    try:
        data = request.get_json()
        iceman_path = data.get('icemanpath', '')
        command_options = data.get('icemancommand', '')
        burnserver = data.get('burnserver', '')

        combin_output_name = (burnserver + command_options.split(" ")[-1]).replace(".", "").replace("", "").replace(":", "")

        if not iceman_path:
            return jsonify({'error': 'Iceman batch file path is required'}), 400
        thread = threading.Thread(target=run_iceman_process, args=(iceman_path, command_options, combin_output_name))
        thread.start()

        threads[combin_output_name] = thread 
        print(threads)
        return jsonify({'status': 'success', 'message': f'Iceman started for {combin_output_name}'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@app.route('/list-threads', methods=['POST'])
def list_threads():
    active_threads = [{'combin_output_name': name, 'is_alive': thread.is_alive()} for name, thread in threads.items()]
    print(active_threads) 
    return jsonify({'threads': active_threads}), 200

@app.route('/stop-thread', methods=['POST'])
def stop_thread():
    data = request.get_json()
    iceman_path = data.get('icemanpath', '')
    command_options = data.get('icemancommand', '')
    burnserver = data.get('burnserver', '')

    combin_output_name = (burnserver + command_options.split(" ")[-1]).replace(".", "").replace("", "").replace(":", "")

    if combin_output_name in processes:
        process = processes[combin_output_name]
        process.terminate()  
        del processes[combin_output_name] 

        if combin_output_name in threads:
            del threads[combin_output_name]

        return jsonify({'status': 'success', 'message': f'Thread {combin_output_name} stopped'}), 200
    else:
        return jsonify({'error': f'Thread {combin_output_name} not found'}), 404

@app.route('/get-logs', methods=['POST'])
def get_logs():
    data = request.get_json()
    iceman_path = data.get('icemanpath', '')
    command_options = data.get('icemancommand', '')
    burnserver = data.get('burnserver', '')
    getburnserver = data.get('burnserver', '').split(":")[0]
    
    combin_output_name = (burnserver + command_options.split(" ")[-1]).replace(".", "").replace("", "").replace(":", "")

    bat_dir = os.path.dirname(iceman_path)
    log_file = os.path.join(bat_dir, f'{combin_output_name}.log')
    print(log_file)

    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            logs = file.read()

        if "ICEman is ready to use." in logs:
            last_core_line = next((line for line in reversed(logs.splitlines()) if "The core #0 listens on" in line), None)
            if last_core_line:
                
                port = last_core_line.split("listens on")[-1].strip().strip(".")
                return jsonify({'status': 'success','burnserver': getburnserver, 'port': port}), 200

        elif "<-- ICEman exit... -->" in logs:
            return jsonify({'logs': logs}), 404
        else:
            return jsonify({'logs': logs}), 404
    else:
        return jsonify({'error': f'Log for {combin_output_name} not found'}), 404

def find_serial_devices():
    """Use PowerShell to find devices with 'Serial' and 'COM' in their names and return their Device IDs"""
    command = """
        Get-WmiObject Win32_PnPEntity | Where-Object { ($_.Name -match 'Serial') -and ($_.Name -match 'COM' -and $_.Description -match 'Serial') } | Select-Object Name, DeviceID, Description | Format-Table -AutoSize
        """
    
    # Run the PowerShell command
    result = subprocess.run(['powershell', '-Command', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Print output and error if any
    print("Output:", result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)

    # Extract and return device IDs from the output
    device_ids = extract_device_ids(result.stdout)
    
    for device_id in device_ids:
        print(f"Attempting to reset device: {device_id}")
        reset_serial_device(device_id)

def extract_device_ids(powershell_output):
    """Extract device IDs from PowerShell output"""
    lines = powershell_output.splitlines()
    device_ids = []

    # Loop through each line to find USB/VID-based device IDs
    for line in lines:
        if 'USB' in line or 'VID' in line:
            parts = line.split()
            for part in parts:
                if ('USB' in part or 'FTDIBUS' in part) and 'VID' in part:
                    device_ids.append(part)
    return device_ids

def reset_serial_device(device_id):
    """Disable and re-enable the device to simulate reset"""
    try:
        # Disable the device
        disable_command = f"Disable-PnpDevice -InstanceId '{device_id}' -Confirm:$false"
        subprocess.run(['powershell', '-Command', disable_command], check=True)
        print(f"Device {device_id} disabled.")

        # Wait for 2 seconds before re-enabling
        time.sleep(2)

        # Enable the device
        enable_command = f"Enable-PnpDevice -InstanceId '{device_id}' -Confirm:$false"
        subprocess.run(['powershell', '-Command', enable_command], check=True)
        print(f"Device {device_id} enabled.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error resetting device {device_id}: {e}")

# API to reset all serial devices
@app.route('/reset-serial-ports', methods=['POST'])
def reset_serial_ports():
    """Endpoint to reset all serial devices found"""
    try:
        find_serial_devices()  # Call function to find and reset serial devices
        return jsonify({'status': 'success', 'message': 'Serial ports reset successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
if __name__ == '__main__':
    # Run the Flask app on port 1234
    app.run(host='0.0.0.0', port=1234, debug=True)
