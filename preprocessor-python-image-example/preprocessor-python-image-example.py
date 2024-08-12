import json
import os
import sys
import socket
import signal
from PIL import Image
import msgpack

# Add the nxai-utilities python utilities
script_location = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(script_location, "../nxai-utilities/python-utilities"))
import communication_utils

# The name of the preprocessor.
# This is used to match the definition of the preprocessor with routing.
Preprocessor_Name = "Python-Example-Preprocessor"

# The socket this preprocessor will listen on.
# This is always given as the first argument when the process is started
# But it can be manually defined as well, as long as it is the same as the socket path in the runtime settings
Preprocessor_Socket_Path = "/tmp/python-example-preprocessor.sock"

# Define a single SHM object to share images back to AI Manager
global output_shm
output_shm = None


def parseImageFromSHM(shm_key: int, width: int, height: int, channels: int):
    global output_shm
    if output_shm is None:
        input_image_size = width * height * channels
        output_shm = communication_utils.create_shm(input_image_size)
        print("Created shm: ", output_shm.id, output_shm.size)

    image_data = communication_utils.read_shm(shm_key)

    # Set all to zero
    # image_data = b"\0" * len(image_data)

    communication_utils.write_shm(output_shm, image_data)

    return output_shm.id


def main():
    # Start socket listener to receive messages from NXAI runtime
    server = communication_utils.startUnixSocketServer(Preprocessor_Socket_Path)
    # Wait for messages in a loop
    while True:
        # Wait for input message from runtime
        try:
            input_message, connection = communication_utils.waitForSocketMessage(server)
        except socket.timeout:
            # Request timed out. Continue waiting
            continue

        image_header = msgpack.unpackb(input_message)
        output_shm_id = parseImageFromSHM(
            image_header["SHMKey"],
            image_header["Width"],
            image_header["Height"],
            image_header["Channels"],
        )

        print("EXAMPLE PREPROCESSOR: Received input message: ", image_header)
        image_header["SHMID"] = output_shm_id

        # Write header to respond
        output_message = msgpack.packb(image_header)

        # Send message back to runtime
        communication_utils.sendMessageOverConnection(connection, output_message)


def signalHandler(sig, _):
    print("EXAMPLE PREPROCESSOR: Received interrupt signal: ", sig)
    # Detach and destroy output shm
    output_shm.detach()
    output_shm.remove()
    sys.exit(0)


if __name__ == "__main__":
    print("EXAMPLE PREPROCESSOR: Input parameters: ", sys.argv)
    # Parse input arguments
    if len(sys.argv) > 1:
        Preprocessor_Socket_Path = sys.argv[1]
    # Handle interrupt signals
    signal.signal(signal.SIGINT, signalHandler)
    # Start program
    main()
