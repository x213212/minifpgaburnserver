open_hw
connect_hw_server

open_hw_target

boot_hw_device  [lindex [get_hw_devices xc7k410t_0] 0]
refresh_hw_device [lindex [get_hw_devices xc7k410t_0] 0]

set current_device [get_hw_devices xc7k410t_0]

refresh_hw_device -update_hw_probes false [lindex $current_device 0]

create_hw_cfgmem -hw_device [lindex $current_device 0] [lindex [get_cfgmem_parts {28f00am29ew-bpi-x16}] 0]

set cfgmem [get_property PROGRAM.HW_CFGMEM [lindex $current_device 0]]
set_property PROGRAM.BLANK_CHECK 0 $cfgmem
set_property PROGRAM.ERASE 1 $cfgmem
set_property PROGRAM.CFG_PROGRAM 1 $cfgmem
set_property PROGRAM.VERIFY 1 $cfgmem
set_property PROGRAM.CHECKSUM 0 $cfgmem

refresh_hw_device [lindex $current_device 0]

set_property PROGRAM.ADDRESS_RANGE {use_file} $cfgmem
set_property PROGRAM.FILES [list "BOARD_BITMAP_PATH"] $cfgmem
set_property PROGRAM.PRM_FILE {} $cfgmem
set_property PROGRAM.BPI_RS_PINS {none} $cfgmem
set_property PROGRAM.UNUSED_PIN_TERMINATION {pull-none} $cfgmem

set_property PROGRAM.BLANK_CHECK 0 $cfgmem
set_property PROGRAM.ERASE 1 $cfgmem
set_property PROGRAM.CFG_PROGRAM 1 $cfgmem
set_property PROGRAM.VERIFY 1 $cfgmem
set_property PROGRAM.CHECKSUM 0 $cfgmem

startgroup
if {![string equal [get_property PROGRAM.HW_CFGMEM_TYPE [lindex $current_device 0]] [get_property MEM_TYPE [get_property CFGMEM_PART [get_property PROGRAM.HW_CFGMEM [lindex $current_device 0]]]]} {
    create_hw_bitstream -hw_device [lindex $current_device 0] [get_property PROGRAM.HW_CFGMEM_BITFILE [lindex $current_device 0]]
    program_hw_devices [lindex $current_device 0]
}
program_hw_cfgmem -hw_cfgmem $cfgmem
endgroup
