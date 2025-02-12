import json
import os
import sys
import socket
import signal
from PIL import Image
import msgpack

# Add the nxai-utilities python utilities
if getattr(sys, "frozen", False):
    script_location = os.path.dirname(sys.executable)
elif __file__:
    script_location = os.path.dirname(__file__)
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
        # Can reuse SHM ( if data is smaller or equal size ) or create new SHM and return ID
        input_image_size = width * height * channels
        output_shm = communication_utils.create_shm(input_image_size)
        print(
            "EXAMPLE PLUGIN Created shm ID: ", output_shm.id, "Size:", output_shm.size
        )

    image_data = communication_utils.read_shm(shm_key)

    # Create new output image
    output_image = bytearray(len(image_data))
    # Mirror and downscale image
    for h_key in range(0, height, 2):
        for w_key in range(0, width, 2):
            output_pixel_index = int(
                ((h_key * width / 4) * channels) + ((w_key / 2) * channels)
            )
            input_pixel_index = (h_key * width * channels) + (
                (width - w_key) * channels
            )
            output_image[output_pixel_index : output_pixel_index + channels] = (
                image_data[input_pixel_index : input_pixel_index + channels]
            )

    communication_utils.write_shm(output_shm, output_image)

    return output_shm.id, int(width / 2), int(height / 2), channels


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
        print("EXAMPLE PREPROCESSOR: Received input message: ", image_header)

        # Process image
        output_shm_id, width, height, channels = parseImageFromSHM(
            image_header["SHMKey"],
            image_header["Width"],
            image_header["Height"],
            image_header["Channels"],
        )

        image_header["SHMID"] = output_shm_id
        image_header["Width"] = width
        image_header["Height"] = height
        image_header["Channels"] = channels

        # Write header to respond
        output_message = msgpack.packb(image_header)

        # Send message back to runtime
        communication_utils.sendMessageOverConnection(connection, output_message)


def signalHandler(sig, _):
    print("EXAMPLE PREPROCESSOR: Received interrupt signal: ", sig)
    # Detach and destroy output shm
    if output_shm is not None:
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
