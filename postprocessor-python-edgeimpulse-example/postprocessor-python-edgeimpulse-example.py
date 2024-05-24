import io
import os
import sys
import socket
import signal
from PIL import Image
import msgpack
import edgeimpulse
from datetime import datetime

# Add the sclbl-utilities python utilities
script_location = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(script_location, "../sclbl-utilities/python-utilities"))
import communication_utils

# The name of the postprocessor.
# This is used to match the definition of the postprocessor with routing.
Postprocessor_Name = "Python-Example-Postprocessor"

# The socket this postprocessor will listen on.
# This is always given as the first argument when the process is started
# But it can be manually defined as well, as long as it is the same as the socket path in the runtime settings
Postprocessor_Socket_Path = "/tmp/python-example-postprocessor.sock"


def main():
    edgeimpulse.API_KEY = ""  # enter your own API_KEY here
    counter = 1

    # Start socket listener to receive messages from NXAI runtime
    server = communication_utils.startUnixSocketServer(Postprocessor_Socket_Path)
    # Wait for messages in a loop
    while True:
        # Wait for input message from runtime
        try:
            input_message, connection = communication_utils.waitForSocketMessage(server)

            image_header = communication_utils.receiveMessageOverConnection(connection)
        except socket.timeout:
            # Did not receive input message or image header
            continue

        # Parse input message
        input_object = communication_utils.parseInferenceResults(input_message)

        # Parse image information
        image_header = msgpack.unpackb(image_header)

        # Decouple training conditions and uploading the sample
        upload_sample = False

        # Trigger the potential training image on condition
        if 'BBoxes_xyxy' in input_object and 'face' in input_object['BBoxes_xyxy'] and len(
                input_object['BBoxes_xyxy']['face']) < 4 * 4:
            print('Less than 4 faces detected')
            upload_sample = True

        # Upload the sample to Edge Impulse
        if upload_sample:
            image_data = communication_utils.read_shm(image_header["SHMKey"])
            with Image.frombytes("RGB", (image_header["Width"], image_header["Height"]), image_data) as image:
                with io.BytesIO() as output:
                    image.save(output, format="JPEG")
                    output.seek(0)
                    filename = "{dt}C{c}.jpg".format(dt=datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), c=counter)
                    contents = output.getvalue()
                    sample = edgeimpulse.experimental.data.Sample(
                        filename=filename,
                        data=output,
                        metadata={
                            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        }
                    )
                    samples = [sample]
                    edgeimpulse.experimental.data.upload_samples(samples)
                    print("Send sample to Edge Impulse: c={c} f={f} l={l}".format(c=counter,f=filename,l=len(contents)))
                    counter += 1

        # Write object back to string
        output_message = communication_utils.writeInferenceResults(input_object)

        # Send message back to runtime
        communication_utils.sendMessageOverConnection(connection, output_message)


def signal_handler(sig, _):
    print("EXAMPLE PLUGIN: Received interrupt signal: ", sig)
    sys.exit(0)


if __name__ == "__main__":
    print("EXAMPLE PLUGIN: Input parameters: ", sys.argv)
    # Parse input arguments
    if len(sys.argv) > 1:
        Postprocessor_Socket_Path = sys.argv[1]
    # Handle interrupt signals
    signal.signal(signal.SIGINT, signal_handler)
    # Start program
    main()
