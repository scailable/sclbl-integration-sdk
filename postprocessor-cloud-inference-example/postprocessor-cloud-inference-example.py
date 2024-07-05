import json
import os
import sys
import socket
import signal
from PIL import Image
import msgpack
import struct
import numpy as np
from aws_utils import classify_faces

# Add the nxai-utilities python utilities
script_location = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(script_location, "../nxai-utilities/python-utilities"))
import communication_utils

# The name of the postprocessor.
# This is used to match the definition of the postprocessor with routing.
Postprocessor_Name = "Python-Example-Postprocessor"

# The socket this postprocessor will listen on.
# This is always given as the first argument when the process is started
# But it can be manually defined as well, as long as it is the same as the socket path in the runtime settings
Postprocessor_Socket_Path = "/tmp/python-example-postprocessor.sock"


def parseImageFromSHM(shm_key: int, width: int, height: int, channels: int):
    try:
        image_data = communication_utils.read_shm(shm_key)
        image_size = width * height * channels
        image_array = list(struct.unpack("B" * image_size, image_data))
        image_array = (
            np.array(image_array).reshape((height, width, channels)).astype("uint8")
        )
    except Exception as e:
        print("Failed to parse image from shared memory: ", e)
        return None

    return image_array


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
            print(
                "EXAMPLE PLUGIN: Did not receive image header. Are the settings correct?"
            )
            continue

        # Parse input message
        input_object = communication_utils.parseInferenceResults(input_message)

        image_header = msgpack.unpackb(image_header)
        image_array = parseImageFromSHM(
            image_header["SHMKey"],
            image_header["Width"],
            image_header["Height"],
            image_header["Channels"],
        )
        if image_array is None:
            continue

        image = Image.fromarray(image_array)

        faces = np.array(input_object["BBoxes_xyxy"]["face"]).reshape(-1, 4)

        faces_to_delete = []
        for i, face in enumerate(faces):
            path = "/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/face.png"
            x1, y1, x2, y2 = face
            cropped_image = image.crop((x1, y1, x2, y2))
            cropped_image.save(path)

            description = classify_faces(path)
            if description is None:
                continue

            # Add the description to the object
            if description not in input_object:
                input_object["BBoxes_xyxy"][description] = face.tolist()
            else:
                input_object["BBoxes_xyxy"][description].extend(face.tolist())

            faces_to_delete.append(i)

            # FIXME: Run the classification for 2 faces max to avoid affecting FPS rate
            if len(faces_to_delete) >= 2:
                break

        # Delete the faces that have been classified
        faces = np.delete(faces, faces_to_delete, axis=0)
        input_object["BBoxes_xyxy"]["face"] = faces.flatten().tolist()

        # Write object back to string
        output_message = communication_utils.writeInferenceResults(input_object)

        # Send message back to runtime
        communication_utils.sendMessageOverConnection(connection, output_message)


def signalHandler(sig, _):
    print("EXAMPLE PLUGIN: Received interrupt signal: ", sig)
    sys.exit(0)


if __name__ == "__main__":
    print("EXAMPLE PLUGIN: Input parameters: ", sys.argv)
    # Parse input arguments
    if len(sys.argv) > 1:
        Postprocessor_Socket_Path = sys.argv[1]
    # Handle interrupt signals
    signal.signal(signal.SIGINT, signalHandler)
    # Start program
    main()
