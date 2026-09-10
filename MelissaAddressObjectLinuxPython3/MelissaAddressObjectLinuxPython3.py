"""
Address Object corrects, verifies and enhances U.S. and Canadian addresses.
Use Address Object to remove bad or incomplete information before it invades your database
and creates a negative impact on your data-driven initiatives. You'll reduce undeliverables,
increase communication efforts, and save money on all your marketing campaigns.

High-level flow of this sample:
  1. SETUP     - create an mdAddr instance, hand it the license string and the paths to
                 the data files, then InitializeDataFiles() (one time).
  2. INPUT     - feed an address in with SetAddress/SetCity/SetState/SetZip.
  3. PROCESS   - VerifyAddress() validates, standardizes, and corrects the address.
  4. READ      - pull the corrected fields back out with the Get* getters
                 (GetAddress, GetCity, GetState, GetZip, GetMelissaAddressKey, ...).
  5. INTERPRET - GetResults() returns comma-separated result codes describing what the
                 object did/found; each code has a human description.

The pieces in this file map onto that flow:
  - run_as_console / parse_arguments : console harness (argument parsing + the interactive loop).
  - AddressObject                    : thin wrapper around mdAddr that owns setup + the call sequence.
  - DataContainer                    : plain holder for one record's input and output.

Where mdAddr comes from:
  The mdAddr class lives in mdAddr_pythoncode.py, a generated Python wrapper over
  libmdAddr.so that the accompanying MelissaAddressObjectLinuxPython3.sh script
  downloads on every run.

Reference:
  Quickstart    : https://docs.melissa.com/on-premise-api/address-object/address-object-quickstart.html
  Release notes : https://releasenotes.melissa.com/on-premise-api/address-object/
  Result codes  : https://docs.melissa.com/on-premise-api/address-object/result-codes.html
"""

import mdAddr_pythoncode
import sys


class DataContainer:
    """Data holder for a single record: carries the input address in and the result codes out."""
    def __init__(self, address="", city="", state="", zip="", result_codes=[]):
        # Input: the street address to process.
        self.address = address

        # Input: the city to process.
        self.city = city

        # Input: the state to process.
        self.state = state

        # Input: the ZIP code to process.
        self.zip = zip

        # Output: comma-separated result codes from GetResults().
        self.result_codes = result_codes


class AddressObject:
    """
    Wrapper that owns a single Melissa Address Object instance and encapsulates the two
    things every Melissa object needs: one-time setup (license + data files) and the
    per-record processing sequence. Reuse one instance across many addresses; do NOT
    re-initialize per address.
    """

    def __init__(self, license, data_path):
        """
        Perform the mandatory one-time setup, in this required order:
          1. SetLicenseString     - authorize the object.
          2. SetPathTo*DataFiles  - tell it where each set of data files lives.
          3. InitializeDataFiles  - load the data into memory.

        Args:
            license: The Melissa license string used to authorize the object.
            data_path: Path to the folder containing the Address Object data files.
        """
        # The underlying Melissa Address Object instance.
        self.md_address_obj = mdAddr_pythoncode.mdAddr()

        # Set license string and set path to data files
        self.md_address_obj.SetLicenseString(license)

        # Path to the Address Object data files.
        self.data_path = data_path

        # Address Object draws on several USPS data sets; point each one at the data folder.
        self.md_address_obj.SetPathToUSFiles(data_path)
        self.md_address_obj.SetPathToAddrKeyDataFiles(data_path)
        self.md_address_obj.SetPathToDPVDataFiles(data_path)
        self.md_address_obj.SetPathToLACSLinkDataFiles(data_path)
        self.md_address_obj.SetPathToRBDIFiles(data_path)
        self.md_address_obj.SetPathToSuiteFinderDataFiles(data_path)
        self.md_address_obj.SetPathToSuiteLinkDataFiles(data_path)

        # Load the data files. The returned ProgramStatus reports whether initialization succeeded.
        # If you see a different date than expected, check your license string and either download the new data files
        # or use the Melissa Updater program to update your data files.
        p_status = self.md_address_obj.InitializeDataFiles()

        # If an issue occurred, please investigate the common causes.
        # Common causes: an invalid/expired license, or missing/wrong-path data files.
        if (p_status != mdAddr_pythoncode.ProgramStatus.ErrorNone):
            print("Failed to Initialize Object.")
            print(p_status)
            return

        # Diagnostic information, handy for confirming the object loaded the data you expect:

        # Build date of the data files
        print(
            f"                DataBase Date: {self.md_address_obj.GetDatabaseDate()}")

        # When the license stops working
        print(
            f"              Expiration Date: {self.md_address_obj.GetLicenseExpirationDate()}")

        # This number should match with the file properties of the Melissa Object binary file.
        # If TEST appears with the build number, there may be a license key issue.
        print(
            f"               Object Version: {self.md_address_obj.GetBuildNumber()}\n")

    def execute_object_and_result_codes(self, data):
        """
        Run the full Address Object processing sequence for one address and capture its
        result codes. This is the canonical per-record call pattern to copy into your own
        application:
          ClearProperties -> SetAddress/SetCity/SetState/SetZip -> VerifyAddress -> GetResults

        Args:
            data: The record to process; its address, city, state, and zip are read as input.

        Returns:
            A DataContainer carrying the same input fields plus this run's result codes.
        """
        # Reset any state left over from a previous address. Important when reusing the same
        # object across multiple records so fields from a prior address don't bleed into this one.
        self.md_address_obj.ClearProperties()

        # Supply the raw input fields to process
        self.md_address_obj.SetAddress(data.address)
        self.md_address_obj.SetCity(data.city)
        self.md_address_obj.SetState(data.state)
        self.md_address_obj.SetZip(data.zip)

        # Validate, standardize, and correct the address
        self.md_address_obj.VerifyAddress()

        # Collect the result codes for this run
        # ResultsCodes explain any issues Address Object has with the object.
        # List of result codes for Address Object
        # https://docs.melissa.com/on-premise-api/address-object/result-codes.html
        result_codes = self.md_address_obj.GetResults()

        return DataContainer(data.address, data.city, data.state, data.zip, result_codes)


def parse_arguments():
    """
    Read the supported command-line options and return them as a (license, test_address,
    test_city, test_state, test_zip, data_path) tuple.

    Recognized flags (each followed by its value, e.g. "--address 22382 Avenida Empresa"):
      --license / -l   : the Melissa license string
      --address / -p   : street address to test in one-shot mode
      --city / -p      : city to test in one-shot mode
      --state / -p     : state to test in one-shot mode
      --zip / -p       : ZIP code to test in one-shot mode

    Note that -p is tested for all four address components, so a -p value is read into
    every one of them; pass the long options to set them individually.
      --dataPath / -d  : path to the Address Object data files

    Returns:
        A (license, test_address, test_city, test_state, test_zip, data_path) tuple, each
        entry empty when its flag was not supplied.
    """
    license, test_address, test_city, test_state, test_zip, data_path = "", "", "", "", "", ""

    args = sys.argv
    index = 0
    for arg in args:

        if (arg == "--license") or (arg == "-l"):
            if (args[index+1] != None):
                license = args[index+1]
        if (arg == "--address") or (arg == "-p"):
            if (args[index+1] != None):
                test_address = args[index+1]
        if (arg == "--city") or (arg == "-p"):
            if (args[index+1] != None):
                test_city = args[index+1]
        if (arg == "--state") or (arg == "-p"):
            if (args[index+1] != None):
                test_state = args[index+1]
        if (arg == "--zip") or (arg == "-p"):
            if (args[index+1] != None):
                test_zip = args[index+1]
        if (arg == "--dataPath") or (arg == "-d"):
            if (args[index+1] != None):
                data_path = args[index+1]
        index += 1

    return (license, test_address, test_city, test_state, test_zip, data_path)


def run_as_console(license, test_address, test_city, test_state, test_zip, data_path):
    """
    Set up the Address Object once, then drive the input -> process -> output cycle.

    In interactive mode (no address args) it loops, asking for a new address each pass
    until the user answers "N". In one-shot mode (address args supplied) it runs a single
    pass and exits.

    Args:
        license: The Melissa license string used to initialize the object.
        test_address: A street address to process in one-shot mode; if empty, the program
            prompts interactively.
        test_city: A city to process in one-shot mode.
        test_state: A state to process in one-shot mode.
        test_zip: A ZIP code to process in one-shot mode.
        data_path: Path to the Address Object data files.
    """
    print("\n\n=========== WELCOME TO MELISSA ADDRESS OBJECT LINUX PYTHON3 ===========\n")

    # Construct the wrapper. This is where the object is licensed, pointed at the data
    # files, and initialized (see the AddressObject constructor above).
    address_object = AddressObject(license, data_path)

    should_continue_running = True

    # Gate the program on a successful initialization. If the data files could not be
    # loaded (bad/expired license, missing or wrong-path data files, ...),
    # GetInitializeErrorString() returns the reason instead of "No error." and we skip
    # the processing loop entirely.
    if address_object.md_address_obj.GetInitializeErrorString() != "No error.":
        should_continue_running = False

    while should_continue_running:
        if (test_address == None or test_address == "") and (test_city == None or test_city == "") and (test_state == None or test_state == "") and (test_state == None or test_state == ""):
            # Interactive mode: prompt the user for each address component.
            print("\nFill in each value to see the Address Object results")
            address = str(input("Address: "))
            city =    str(input("City: "))
            state =   str(input("State: "))
            zip =     str(input("Zip: "))
        else:
            # One-shot mode: use the address passed on the command line.
            address = test_address
            city = test_city
            state = test_state
            zip = test_zip

        # Holder for this pass's input and result codes.
        data = DataContainer(address, city, state, zip)

        # Print user input
        print("\n=============================== INPUTS ================================\n")
        print(f"                      Address: {data.address}")
        print(f"                         City: {data.city}")
        print(f"                        State: {data.state}")
        print(f"                          Zip: {data.zip}")

        # Execute Address Object
        # Runs the verify sequence and returns the result codes.
        data_container = address_object.execute_object_and_result_codes(data)

        # Print output
        # Each Get* getter below returns one component the object produced for the most
        # recently processed address. These read directly from the mdAddr instance, which
        # still holds the results from the Execute call above.
        print("\n=============================== OUTPUT ================================\n")
        print("\n\tAddress Object Information:")

        print(
            f"\t                          MAK: {address_object.md_address_obj.GetMelissaAddressKey()}")
        print(
            f"\t               Address Line 1: {address_object.md_address_obj.GetAddress()}")
        print(
            f"\t               Address Line 2: {address_object.md_address_obj.GetAddress2()}")
        print(
            f"\t                         City: {address_object.md_address_obj.GetCity()}")
        print(
            f"\t                        State: {address_object.md_address_obj.GetState()}")
        print(
            f"\t                          Zip: {address_object.md_address_obj.GetZip()}")

        print(
            f"\t                 Result Codes: {data_container.result_codes}")

        # Result codes come back as a single comma-separated string (e.g. "AS01,AC01").
        # Split it and ask the object for a readable description of each code.
        # ResultCodeDescriptionLong requests the long-form text; a short form is also
        # available via ResultCodeDescriptionShort
        rs = data_container.result_codes.split(',')
        for r in rs:
            print(
                f"        {r}: {address_object.md_address_obj.GetResultCodeDescription(r, mdAddr_pythoncode.ResultCdDescOpt.ResultCodeDescriptionLong)}")

        is_valid = False

        # In one-shot mode there is nothing more to do after a single pass: mark the
        # input handled and stop the outer loop.
        if not (test_address == None or test_address == ""):
            is_valid = True
            should_continue_running = False

        # Interactive mode: ask whether to process another address. Keep prompting until
        # we get a valid Y/N. "N" ends the program; "Y" falls through to another pass.
        while not is_valid:

            test_another_response = input(
                str("\nTest another address? (Y/N)\n"))

            if not (test_another_response == None or test_another_response == ""):
                test_another_response = test_another_response.lower()
            if test_another_response == "y":
                is_valid = True

            elif test_another_response == "n":
                is_valid = True
                should_continue_running = False
            else:

                print("Invalid Response, please respond 'Y' or 'N'")

    print("\n============= THANK YOU FOR USING MELISSA PYTHON3 OBJECT ==============\n")


# ---------------------------- MAIN STARTS HERE ----------------------------

# Read the optional command-line arguments, then hand control to run_as_console, which
# performs the actual Address Object setup and processing.
license, test_address, test_city, test_state, test_zip, data_path = parse_arguments()

run_as_console(license, test_address, test_city, test_state, test_zip, data_path)
