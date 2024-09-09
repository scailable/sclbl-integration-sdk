import os
import sys
import socket
import signal
import logging
# from pprint import pformat

# Add the sclbl-utilities python utilities
script_location = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(script_location, "../sclbl-utilities/python-utilities"))
import communication_utils

# Set up logging
LOG_FILE = ("/opt/networkoptix-metavms/mediaserver/bin/plugins/"
            "nxai_plugin/nxai_manager/etc/plugin.example.log")

# Initialize plugin and logging, script makes use of INFO and DEBUG levels
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - example - %(message)s',
                    filename=LOG_FILE, filemode="w")
logging.debug("Initializing example plugin")

# The name of the postprocessor.
# This is used to match the definition of the postprocessor with routing.
Postprocessor_Name = "Python-Example-Postprocessor"

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
        logging.debug("Waiting for input message")

        try:
            input_message, connection = communication_utils.waitForSocketMessage(server)
        except socket.timeout:
            # Request timed out. Continue waiting
            logging.debug("Socket timed out")
            continue

        logging.debug("Received input message")

        # Parse input message
        input_object = communication_utils.parseInferenceResults(input_message)

        # Use pformat to format the deep object
        # formatted_unpacked_object = pformat(input_object)
        # logging.debug(f'Unpacked:\n\n{formatted_unpacked_object}\n\n')

        # Add extra bbox
        if "BBoxes_xyxy" not in input_object:
            input_object["BBoxes_xyxy"] = {}
        input_object["BBoxes_xyxy"]["test"] = [100.0, 100.0, 200.0, 200.0]

        # Use pformat to format the deep object
        # formatted_packed_object = pformat(input_object)
        # logging.debug(f'Packing:\n\n{formatted_packed_object}\n\n')

        # Write object back to string
        output_message = communication_utils.writeInferenceResults(input_object)

        # Send message back to runtime
        communication_utils.sendMessageOverConnection(connection, output_message)


def signalHandler(sig, _):
    logging.debug("Received interrupt signal: " + str(sig))
    sys.exit(0)


if __name__ == "__main__":
    logging.debug("Input parameters: " + str(sys.argv))
    # Parse input arguments
    if len(sys.argv) > 1:
        Postprocessor_Socket_Path = sys.argv[1]
    # Handle interrupt signals
    signal.signal(signal.SIGINT, signalHandler)
    # Start program
    try:
        main()
    except Exception as e:
        logging.error(e, exc_info=True)