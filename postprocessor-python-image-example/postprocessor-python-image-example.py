import json
import os
import sys
import socket
import signal
import logging
import io
import time
from pprint import pformat
import msgpack
import struct
from math import prod
from datetime import datetime
from PIL import Image
import msgpack

# Add the sclbl-utilities python utilities
script_location = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(script_location, "../sclbl-utilities/python-utilities"))

# Set up logging
LOG_FILE = ("/opt/networkoptix-metavms/mediaserver/bin/plugins/"
            "nxai_plugin/nxai_manager/etc/plugin.log")


# Initialize plugin and logging, script makes use of INFO and DEBUG levels
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=LOG_FILE, filemode="w")
logging.debug("IMAGE EXAMPLE PLUGIN: Initializing plugin")

import communication_utils

# The name of the postprocessor.
# This is used to match the definition of the postprocessor with routing.
Postprocessor_Name = "Python-Image-Example-Postprocessor"

# The socket this postprocessor will listen on.
# This is always given as the first argument when the process is started
# But it can be manually defined as well, as long as it is the same as the socket path in the runtime settings
Postprocessor_Socket_Path = "/tmp/python-example-postprocessor.sock"


def parseImageFromSHM(shm_key: int, width: int, height: int, channels: int):
    image_data = communication_utils.read_shm(shm_key)

    cumulative = 0
    for b in image_data:
        cumulative += b

    return cumulative

def main():
    # Start socket listener to receive messages from NXAI runtime
    server = communication_utils.startUnixSocketServer(Postprocessor_Socket_Path)
    # Wait for messages in a loop
    while True:
        # Wait for input message from runtime
        try:
            input_message, connection = communication_utils.waitForSocketMessage(server)
        except socket.timeout:
            # Request timed out. Continue waiting
            continue

        # Since we're also expecting an image, receive the image header
        try:
            image_header = communication_utils.receiveMessageOverConnection(connection)
        except socket.timeout:
            # Did not receive image header
            logging.debug("IMAGE EXAMPLE PLUGIN: Did not receive image header. Are the settings correct?")
            continue

        # Parse input message
        input_object = communication_utils.parseInferenceResults(input_message)

        formatted_unpacked_object = pformat(input_object)
        logging.debug(f'IMAGE EXAMPLE PLUGIN: Unpacked:\n\n{formatted_unpacked_object}\n\n')

        image_header = msgpack.unpackb(image_header)
        print(image_header)
        cumulative = parseImageFromSHM(
            image_header["SHMKey"],
            image_header["Width"],
            image_header["Height"],
            image_header["Channels"],
        )

        # Add extra bbox
        if "Counts" not in input_object:
            input_object["Counts"] = {}
        input_object["Counts"]["ImageBytesCumalitive"] = cumulative

        logging.debug("IMAGE EXAMPLE PLUGIN: Received input message: " + input_message)

        formatted_packed_object = pformat(input_object)
        logging.debug(f'IMAGE EXAMPLE PLUGIN: Packing:\n\n{formatted_packed_object}\n\n')

        # Write object back to string
        output_message = communication_utils.writeInferenceResults(input_object)

        # Send message back to runtime
        communication_utils.sendMessageOverConnection(connection, output_message)


def signalHandler(sig, _):
    logging.debug("IMAGE EXAMPLE PLUGIN: Received interrupt signal: " + str(sig))
    sys.exit(0)


if __name__ == "__main__":
    logging.debug("IMAGE EXAMPLE PLUGIN: Input parameters: " + str(sys.argv))
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
