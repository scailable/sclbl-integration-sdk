import os
import sys
import socket
import signal
from pprint import pformat
import logging

# Add the sclbl-utilities python utilities
script_location = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(script_location, "../sclbl-utilities/python-utilities"))
import communication_utils

# Set up logging
LOG_FILE = ("/opt/networkoptix-metavms/mediaserver/bin/plugins/"
            "nxai_plugin/nxai_manager/etc/plugin.log")


# Initialize plugin and logging, script makes use of INFO and DEBUG levels
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=LOG_FILE, filemode="w")
logging.debug("NORESPONSE EXAMPLE PLUGIN: Initializing plugin")

# The name of the postprocessor.
# This is used to match the definition of the postprocessor with routing.
Postprocessor_Name = "Python-NoResponse-Example-Postprocessor"

# The socket this postprocessor will listen on.
# This is always given as the first argument when the process is started
# But it can be manually defined as well, as long as it is the same as the socket path in the runtime settings
Postprocessor_Socket_Path = "/tmp/python-example-postprocessor.sock"

# Data Types
# 1:  //FLOAT
# 2:  //UINT8
# 3:  //INT8
# 4:  //UINT16
# 5:  //INT16
# 6:  //INT32
# 7:  //INT64
# 8:  //STRING
# 9:  //BOOL
# 11: //DOUBLE
# 12: //UINT32
# 13: //UINT64


def main():
    # Start socket listener to receive messages from NXAI runtime
    server = communication_utils.startUnixSocketServer(Postprocessor_Socket_Path)
    # Wait for messages in a loop
    while True:
        # Wait for input message from runtime
        try:
            input_message, _ = communication_utils.waitForSocketMessage(server)
        except socket.timeout:
            # Request timed out. Continue waiting
            continue

        logging.debug("NORESPONSE EXAMPLE PLUGIN: Received input message: " + input_message)

        # Parse input message
        input_object = communication_utils.parseInferenceResults(input_message)

        formatted_unpacked_object = pformat(input_object)
        logging.debug(f'NORESPONSE EXAMPLE PLUGIN: Unpacked:\n\n{formatted_unpacked_object}\n\n')

def signalHandler(sig, _):
    logging.debug("NORESPONSE EXAMPLE PLUGIN: Received interrupt signal: " + str(sig))
    sys.exit(0)


if __name__ == "__main__":
    logging.debug("NORESPONSE EXAMPLE PLUGIN: Input parameters: " + str(sys.argv))
    # Parse input arguments
    if len(sys.argv) > 1:
        Postprocessor_Socket_Path = sys.argv[1]
    # Handle interrupt signals
    signal.signal(signal.SIGINT, signalHandler)
    # Start program
    main()
