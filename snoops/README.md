
To snoop: 

On the Android device:
1. Install the MI Matrix Panel app 
1. Enable development mode 
1. Enable Bluetooth HCI snoop log in the Developer options menu
1. Restart Bluetooth 
1. Run the app a little
1. Enable USB debugging

On a computer:
1. Install adb
1. Connect Android device using cable
1. Run `./adb bugreport bugreport.zip`
1. Unzip zip
1. Log is in bugreport/FS/data/misc/bluetooth/logs/btsnoop_hci.log
1. Install Wireshark
1. Open file with Wireshark
1. Filter: btatt
1. Select the interesting messages
1. Select File/Export Packet Dissections/As plain text...
1. Options: Selected packets only and don't forget Bytes to get the complete messages
