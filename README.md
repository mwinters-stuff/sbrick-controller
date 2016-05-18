# sbrick-controller
Python application to control a SBrick

You will need the python packages: 
 * bluepy
 * simplejson
And PyGtk

# Edit config.json
This file is a list of your sbricks and whats connected to them.
See the supplied file for the format.

# Run it
python main.py

# scanning for ble devices.
Use scanner.py as root to scan.
> sudo python scanner.py


# Mmmm.
Use the class SBrickCommunications in SBrickCommunications.py in your own programs.

