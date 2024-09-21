open_hw
connect_hw_server
open_hw_target
boot_hw_device  [lindex [get_hw_devices xc7k410t_0] 0]
refresh_hw_device [lindex [get_hw_devices xc7k410t_0] 0]
set current_device [get_hw_devices xc7k410t_0]

refresh_hw_device -update_hw_probes false [lindex $current_device 0]
set_property PROBES.FILE {} [get_hw_devices xc7k410t_0]
set_property FULL_PROBES.FILE {} [get_hw_devices xc7k410t_0]
set_property PROGRAM.FILE {BOARD_BITMAP_PATH} [get_hw_devices xc7k410t_0]
program_hw_devices [get_hw_devices xc7k410t_0]
refresh_hw_device [lindex [get_hw_devices xc7k410t_0] 0]

q
y
