#!/bin/bash

# MelissaAddressObjectLinuxPython3
#
# Downloads the required components and then runs MelissaAddressObjectLinuxPython3.
#
# This script uses the Melissa Updater to fetch the data file(s), the shared object, and the
# Python wrapper, verifies the shared object downloaded, then runs the Python script against
# the supplied address.
#
# Overall flow:
#   1. Read parameters / prompt for the license and data path.
#   2. Download data file(s), the shared object, and the wrapper via the Melissa Updater.
#   3. Confirm the shared object is present.
#   4. Run the script (single test address or interactive).
#
# Options:
#   --address <value>   Street address to verify.
#   --city <value>      City for the address to verify.
#   --state <value>     State/province for the address to verify.
#   --zip <value>       ZIP/postal code for the address to verify.
#   --dataPath <value>  Path to an existing data files directory. If omitted, the script
#                       prompts for a path; pressing Enter at that prompt skips it and
#                       downloads the data files into the project's Data folder via the
#                       Melissa Updater. A path that does not exist aborts the script.
#   --license <value>   License string. Resolved in this order:
#                         1. This option.
#                         2. An interactive prompt, if the option was not supplied.
#                         3. The MD_LICENSE environment variable, if the prompt was left blank.
#                       Note that the environment variable is the last resort, not the first:
#                       running without --license always prompts, even when MD_LICENSE is set.
#   --quiet             Suppresses the Melissa Updater console output during downloads.
#
# Examples:
#   ./MelissaAddressObjectLinuxPython3.sh --license "your-license"
#   ./MelissaAddressObjectLinuxPython3.sh --address "22382 Avenida Empresa" --city "Rancho Santa Margarita" --state "CA" --zip "92688" --license "your-license"

######################### Constants ##########################

RED='\033[0;31m' #RED
NC='\033[0m' # No Color

######################### Parameters ##########################

address=""
city=""
state=""
zip=""
dataPath=""
license=""
quiet="false"

while [ $# -gt 0 ] ; do
  case $1 in
    --address) 
        address="$2"

        if [ "$address" == "--city" ] || [ "$address" == "--state" ] || [ "$address" == "--zip" ] || [ "$address" == "--dataPath" ] || [ "$address" == "--license" ] || [ "$address" == "--quiet" ] || [ -z "$address" ];
        then
            printf "${RED}Error: Missing an argument for parameter \'address\'.${NC}\n"  
            exit 1
        fi  
        ;;
	--city) 
        city="$2"

        if [ "$city" == "--address" ] || [ "$city" == "--state" ] || [ "$city" == "--zip" ] || [ "$city" == "--dataPath" ] || [ "$city" == "--license" ] || [ "$city" == "--quiet" ] || [ -z "$city" ];
        then
            printf "${RED}Error: Missing an argument for parameter \'city\'.${NC}\n"  
            exit 1
        fi  
        ;;
	--state) 
        state="$2"

        if [ "$state" == "--city" ] || [ "$state" == "--address" ] || [ "$state" == "--zip" ] || [ "$state" == "--dataPath" ] || [ "$state" == "--license" ] || [ "$state" == "--quiet" ] || [ -z "$state" ];
        then
            printf "${RED}Error: Missing an argument for parameter \'state\'.${NC}\n"  
            exit 1
        fi   
        ;;
	--zip) 
        zip="$2"

        if [ "$zip" == "--city" ] || [ "$zip" == "--state" ] || [ "$zip" == "--address" ] || [ "$zip" == "--dataPath" ] ||  [ "$zip" == "--license" ] || [ "$zip" == "--quiet" ] || [ -z "$zip" ];
        then
            printf "${RED}Error: Missing an argument for parameter \'zip\'.${NC}\n"  
            exit 1
        fi   
        ;;		
    --dataPath) 
        dataPath="$2"

        if [ "$dataPath" == "--address" ] || [ "$dataPath" == "--city" ] || [ "$dataPath" == "--state" ] || [ "$dataPath" == "--zip" ] || [ "$dataPath" == "--license" ] || [ "$dataPath" == "--quiet" ] || [ -z "$dataPath" ];
        then
            printf "${RED}Error: Missing an argument for parameter \'dataPath\'.${NC}\n"  
            exit 1
        fi   
        ;;
    --license) 
        license="$2"

        if [ "$license" == "--city" ] || [ "$license" == "--state" ] || [ "$license" == "--zip" ] || [ "$license" == "--address" ] || [ "$license" == "--dataPath" ] || [ "$license" == "--quiet" ] || [ -z "$license" ];
        then
            printf "${RED}Error: Missing an argument for parameter \'license\'.${NC}\n"  
            exit 1
        fi    
        ;;
    --quiet) 
        quiet="true" 
        ;;
  esac
  shift
done

######################### Config ###########################

# Product release the updater pulls files for
RELEASE_VERSION='2026.08'
ProductName="DQ_ADDR_DATA"

# Uses the location of the .sh file 
CurrentPath=$(pwd)
ProjectPath="$CurrentPath/MelissaAddressObjectLinuxPython3"

if [ -z "$dataPath" ];
then
    DataPath="$ProjectPath/Data"
else
    DataPath=$dataPath
fi

if [ ! -d "$DataPath" ] && [ "$DataPath" == "$ProjectPath/Data" ];
then
    mkdir "$DataPath"
elif [ ! -d "$DataPath" ] && [ "$DataPath" != "$ProjectPath/Data" ];
then
    printf "\nData file path does not exist. Please check that your file path is correct.\n"
    printf "\nAborting program, see above.\n"
    exit 1
fi

# Binary/shared object needed to run the example
Config_FileName="libmdAddr.so"
Config_ReleaseVersion=$RELEASE_VERSION
Config_OS="LINUX"
Config_Compiler="GCC48"
Config_Architecture="64BIT"
Config_Type="BINARY"

# Python wrapper source that exposes the shared object to the script
Wrapper_FileName="mdAddr_pythoncode.py"
Wrapper_ReleaseVersion=$RELEASE_VERSION
Wrapper_OS="ANY"
Wrapper_Compiler="PYTHON"
Wrapper_Architecture="ANY"
Wrapper_Type="INTERFACE"

######################## Functions #########################

# Download the product data file(s) into $DataPath via the Melissa Updater.
DownloadDataFiles()
{
    printf "============================ MELISSA UPDATER ==========================\n"
    printf "MELISSA UPDATER IS DOWNLOADING DATA FILE(S)...\n"

    ./MelissaUpdater/MelissaUpdater manifest -p $ProductName -r $RELEASE_VERSION -l $1 -t $DataPath 

    if [ $? -ne 0 ];
    then
        printf "\nCannot run Melissa Updater. Please check your license string!\n"
        exit 1
    fi     
    
    printf "Melissa Updater finished downloading data file(s)!\n"
}

# Download the shared object into the project folder.
DownloadSO() 
{
    printf "\nMELISSA UPDATER IS DOWNLOADING SO(S)...\n"
    
    # Check for quiet mode
    if [ $quiet == "true" ];
    then
        ./MelissaUpdater/MelissaUpdater file --filename $Config_FileName --release_version $Config_ReleaseVersion --license $1 --os $Config_OS --compiler $Config_Compiler --architecture $Config_Architecture --type $Config_Type --target_directory $ProjectPath &> /dev/null
        if [ $? -ne 0 ];
        then
            printf "\nCannot run Melissa Updater. Please check your license string!\n"
            exit 1
        fi
    else
        ./MelissaUpdater/MelissaUpdater file --filename $Config_FileName --release_version $Config_ReleaseVersion --license $1 --os $Config_OS --compiler $Config_Compiler --architecture $Config_Architecture --type $Config_Type --target_directory $ProjectPath 
        if [ $? -ne 0 ];
        then
            printf "\nCannot run Melissa Updater. Please check your license string!\n"
            exit 1
        fi
    fi
    
    printf "Melissa Updater finished downloading $Config_FileName!\n"
}

# Download the Python wrapper source into the project folder.
DownloadWrapper() 
{
    printf "\nMELISSA UPDATER IS DOWNLOADING WRAPPER(S)...\n"
    
    # Check for quiet mode
    if [ $quiet == "true" ];
    then
        ./MelissaUpdater/MelissaUpdater file --filename $Wrapper_FileName --release_version $Wrapper_ReleaseVersion --license $1 --os $Wrapper_OS --compiler $Wrapper_Compiler --architecture $Wrapper_Architecture --type $Wrapper_Type --target_directory $ProjectPath &> /dev/null
        if [ $? -ne 0 ];
        then
            printf "\nCannot run Melissa Updater. Please check your license string!\n"
            exit 1
        fi
    else
        ./MelissaUpdater/MelissaUpdater file --filename $Wrapper_FileName --release_version $Wrapper_ReleaseVersion --license $1 --os $Wrapper_OS --compiler $Wrapper_Compiler --architecture $Wrapper_Architecture --type $Wrapper_Type --target_directory $ProjectPath 
        if [ $? -ne 0 ];
        then
            printf "\nCannot run Melissa Updater. Please check your license string!\n"
            exit 1
        fi
    fi
    
    printf "Melissa Updater finished downloading $Wrapper_FileName!\n"
}

# Verify the expected shared object landed in the project folder
CheckSOs() 
{
    if [ ! -f $ProjectPath/$Config_FileName ];
    then
        echo "false"
    else
        echo "true"
    fi
}

########################## Main ############################

printf "\n======================== Melissa Address Object =======================\n                      [ Python3 | Linux | 64BIT ]\n"

# Get license (either from parameters or user input)
if [ -z "$license" ];
then
  printf "Please enter your license string: "
  read license
fi

# Check for License from Environment Variables 
if [ -z "$license" ];
then
  license=`echo $MD_LICENSE` 
fi

if [ -z "$license" ];
then
  printf "\nLicense String is invalid!\n"
  exit 1
fi

# Get data file path (either from parameters or user input)
if [ "$DataPath" = "$ProjectPath/Data" ]; then
    printf "Please enter your data files path directory if you have already downloaded the release zip.\nOtherwise, the data files will be downloaded using the Melissa Updater (Enter to skip): "
    read dataPathInput

    if [ ! -z "$dataPathInput" ]; then  
        if [ ! -d "$dataPathInput" ]; then  
            printf "\nData file path does not exist. Please check that your file path is correct.\n"
            printf "\nAborting program, see above.\n"
            exit 1
        else
            DataPath=$dataPathInput
        fi
    fi
fi

# Use Melissa Updater to download data file(s) 
# Download data file(s) 
DownloadDataFiles $license # Comment out this line if using own DQS release

# Download SO(s)
DownloadSO $license 

# Download wrapper(s)
DownloadWrapper $license

# Check if all SO(s) have been downloaded. Exit script if missing
printf "\nDouble checking SO file(s) were downloaded...\n"

SOsAreDownloaded=$(CheckSOs)

if [ "$SOsAreDownloaded" == "false" ];
then
    printf "\n$Config_FileName not found"
    printf "\nMissing the above data file(s).  Please check that your license string and directory are correct.\n"

    printf "\nAborting program, see above.\n"
    exit 1
fi

printf "\nAll file(s) have been downloaded/updated!\n"

# Start
# Run Project
# No address supplied -> run interactively; otherwise pass the address in.
# LD_LIBRARY_PATH is extended first so the interpreter can load the shared object.
if [ -z "$address" ] && [ -z "$city" ] && [ -z "$state" ] && [ -z "$zip" ];
then
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:./MelissaAddressObjectLinuxPython3
    python3 $ProjectPath/MelissaAddressObjectLinuxPython3.py --license $license --dataPath $DataPath
else
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:./MelissaAddressObjectLinuxPython3
    python3 $ProjectPath/MelissaAddressObjectLinuxPython3.py --license $license --dataPath $DataPath --address "$address" --city "$city" --state "$state" --zip "$zip"
fi
