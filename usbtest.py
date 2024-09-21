import subprocess
import time
def check_powershell():
    command = """
        Get-WmiObject Win32_PnPEntity | Where-Object { ($_.Name -match 'Serial') -and ($_.Name -match 'COM' -and $_.Description -match 'Serial') } | Select-Object Name, DeviceID, Description | Format-Table -AutoSize
        """
    
    result = subprocess.run(['powershell', '-Command', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    print("Output:", result.stdout)

    if result.stderr:
        print("Errors:", result.stderr)

    device_ids = extract_device_ids(result.stdout)
    
    for device_id in device_ids:
        print(f"Attempting to reset device: {device_id}")
        reset_device(device_id)

def extract_device_ids(output):
    lines = output.splitlines()
    device_ids = []

    for line in lines:
        if 'USB' in line or line.find("VID")>=0:  
            parts = line.split()

            for part in parts:
                if ('USB' in part or 'FTDIBUS' in part) and part.find("VID")>=0:
                    device_ids.append(part)
    return device_ids

def reset_device(device_id):
    try:
        disable_command = f"Disable-PnpDevice -InstanceId '{device_id}' -Confirm:$false"
        subprocess.run(['powershell', '-Command', disable_command], check=True)
        print(f"USB device {device_id} disabled.")

        time.sleep(2)

        enable_command = f"Enable-PnpDevice -InstanceId '{device_id}' -Confirm:$false"
        subprocess.run(['powershell', '-Command', enable_command], check=True)
        print(f"USB device {device_id} enabled.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error resetting USB device: {e}")

check_powershell()
