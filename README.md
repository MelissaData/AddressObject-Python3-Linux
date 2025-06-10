# Melissa - Address Object Linux Python3

## Purpose

This code showcases the Melissa Address Object using Python3.

Please feel free to copy or embed this code to your own project. Happy coding!

For the latest Melissa Address Object release notes, please visit: https://releasenotes.melissa.com/on-premise-api/address-object/

For further details, please visit: https://docs.melissa.com/on-premise-api/address-object/address-object-quickstart.html

The console will ask the user for:

- Address
- City
- State
- Zip

And return 

- Melissa Address Key (MAK)
- Address Line 1
- Address Line 2
- City
- State
- Zip
- Result Codes

## Tested Environments

- Linux 64-bit Python 3.8.7, Ubuntu 20.04.05 LTS
- Melissa data files for 2025-06

## Required File(s) and Programs

#### libmdAddr.so

This is the c++ code of the Melissa Object.

#### Data File(s)
- Addr.dbf
- Congress.csv
- dph256.dte
- dph256.hsa
- dph256.hsc
- dph256.hsf
- dph256.hsn
- dph256.hsv
- dph256.hsx
- ews.txt
- lcd256
- mdAddr.dat
- mdAddr.lic
- mdAddr.nat
- mdAddr.str
- mdAddrKey.db
- mdAddrKeyCA.db
- mdCanada3.db
- mdCanadaPOC.db
- mdLACS256.dat
- mdRBDI.dat
- mdSteLink256.dat
- mdSuiteFinder.db
- month256.dat

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

This project is compatible with Python3

#### Install Python3
Before starting, make sure that Python3 has been correctly installed on your machine and your environment paths are configured. 

You can download Python here: 
https://www.python.org/downloads/

You can check that your environment is set up correctly by opening a command prompt window and typing the following:
`python3 --version`

![alt text](/screenshots/python_version.PNG)

If you see the version number then you have installed Python3 and set up your environment paths correctly!

----------------------------------------

#### Download this project
```
git clone https://github.com/MelissaData/AddressObject-Python3-Linux
cd AddressObject-Python3-Linux
```

#### Set up Melissa Updater 


Melissa Updater is a CLI application allowing the user to update their Melissa applications/data. 

- In the root directory of the project, create a folder called `MelissaUpdater` by using the command: 

  `mkdir MelissaUpdater`

- Enter the newly created folder using the command:

  `cd MelissaUpdater`

- Proceed to install the Melissa Updater using the curl command: 

  `curl -L -O https://releases.melissadata.net/Download/Library/LINUX/NET/ANY/latest/MelissaUpdater`

- After the Melissa Updater is installed, you will need to change the Melissa Updater to an executable using the command:

  `chmod +x MelissaUpdater`

- Now that the Melissa Updater is set up, you can now proceed to move back into the project folder by using the command:
  
   `cd ..`

----------------------------------------

#### Different ways to get data file(s)
1.  Using Melissa Updater
    - It will handle all of the data download/path and .so file(s) for you. 
2.  If you already have the latest DQS release zip, you can find the data file(s) in there
    - To pass in your own data file path directory, you may either use the '--dataPath' parameter or enter the data file path directly in interactive mode.
    - Comment out this line "DownloadDataFiles $license" in the bash script.
    - This will prevent you from having to redownload all the files.
	
----------------------------------------
### Change Bash Script Permissions
To be able to run the bash script, you must first make it an executable using the command:

`chmod +x MelissaAddressObjectLinuxPython3.sh`

Then you need to add permissions to the build directory with the command:

`chmod +rwx MelissaAddressObjectLinuxPython3`

As an indicator, the filename will change colors once it becomes an executable.

You may also need to alter permissions for the python files. To do this navigate into the MelissaAddressObjectLinuxPython3 directory and run these commands: \
`chmod +rx MelissaAddressObjectLinuxPython3/MelissaAddressObjectLinuxPython3.py` \
`chmod +rx MelissaAddressObjectLinuxPython3/mdAddr_pythoncode.py`

## Run Bash Script

Parameters:
- --address: a test street address (house number & street name)
- --city (optional): a test city
- --state (optional): a test state
- --zip (optional): a test zip code
 	
  These are convenient when you want to get results for a specific address in one run instead of testing multiple addresses in interactive mode.  

- --dataPath (optional): a data file path directory to test the Address Object
- --license (optional): a license string to test the Address Object
- --quiet (optional): add to the command if you do not want to get any console output from the Melissa Updater

- Interactive 

  The script will prompt the user for an address, city, state, and zip, then use the provided inputs to test Address Object. For example:
  ```
  ./MelissaAddressObjectLinuxPython3.sh
  ```
  For quiet mode:
  ```
  ./MelissaAddressObjectLinuxPython3.sh -quiet
  ```
- Command Line 

  You can pass an address, city, state, zip, and a license string into the ```--address```, ```--city```, ```--state```, ```--zip```, and ```--license``` parameters respectively to test Address Object. For example:

  With all parameters:
  ```
  ./MelissaAddressObjectLinuxPython3.sh --address "22382 Avenida Empresa" --city "Rancho Santa Margarita" --state "CA" --zip "92688"
  ./MelissaAddressObjectLinuxPython3.sh --address "22382 Avenida Empresa" --city "Rancho Santa Margarita" --state "CA" --zip "92688" --license "<your_license_string>"
  ```

  With any known (optional) parameters:
  ```
  ./MelissaAddressObjectLinuxPython3.sh --address "22382 Avenida Empresa" --state "CA" 
  ./MelissaAddressObjectLinuxPython3.sh --address "22382 Avenida Empresa" --state "CA" --license "<your_license_string>"
  ```

  For quiet mode:
  ```
  ./MelissaAddressObjectLinuxPython3.sh --address "22382 Avenida Empresa" --city "Rancho Santa Margarita" --state "CA" --zip "92688" --quiet
  ./MelissaAddressObjectLinuxPython3.sh --address "22382 Avenida Empresa" --city "Rancho Santa Margarita" --state "CA" --zip "92688" --license "<your_license_string>" --quiet
  ```
This is the expected output of a successful setup for interactive mode:

![alt text](/screenshots/output.PNG)

    
## Troubleshooting

Troubleshooting for errors found while running your program.

### Errors:

| Error      | Description |
| ----------- | ----------- |
| ErrorRequiredFileNotFound      | Program is missing a required file. Please check your Data folder and refer to the list of required files above. If you are unable to obtain all required files through the Melissa Updater, please contact technical support below. |
| ErrorLicenseExpired   | Expired license string. Please contact technical support below. |

## Contact Us

For free technical support, please call us at 800-MELISSA ext. 4
(800-635-4772 ext. 4) or email us at tech@melissa.com.

To purchase this product, contact the Melissa sales department at
800-MELISSA ext. 3 (800-635-4772 ext. 3).
