import io
import os
import sys
import socket
import signal
import time

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

# We keep a counter to generate unique filenames.
samples_counter: int = 0

# The buffer with samples to batch.
samples_buffer: list = []

# Flush the buffer at this length
samples_buffer_flush_size = 20


def send_samples_buffer():
    # This function sends the buffered samples to an Edge Impulse instance for data processing.
    # It generates a unique filename for each sample and adds it to a new list of samples while
    # updating the global counter.
    # It then uploads all these samples to the Edge Impulse. The function also times the duration of
    # the upload and prints this time along with the number of samples uploaded. If the sample buffer
    # was already empty, the function just prints that there were no samples to upload.
    # At the end, it empties the sample buffer.
    global samples_buffer, samples_counter
    if len(samples_buffer) > 0:
        print("Sending {c} samples to Edge Impulse...".format(c=len(samples_buffer)))
        start_at = time.perf_counter()
        samples = []
        for contents in samples_buffer:
            samples_counter += 1
            filename = "{dt}C{c}.jpg".format(dt=datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), c=samples_counter)
            output = io.BytesIO(contents)
            sample = edgeimpulse.experimental.data.Sample(
                filename=filename,
                data=output,
                metadata={
                    "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                }
            )
            samples.append(sample)

        edgeimpulse.experimental.data.upload_samples(samples)
        end_at = time.perf_counter()
        print("Send {c} samples in {d:0.1f}sec to Edge Impulse. Total {t}".format(
            c=len(samples_buffer), d=end_at-start_at, t=samples_counter,
        ))
        # print("Send a total of {t} samples to Edge Impulse".format(t=samples_counter))

        samples_buffer = []
    else:
        print("No samples to send to Edge Impulse. Total {t}".format(t=samples_counter))


def main():
    global samples_buffer
    global samples_counter

    edgeimpulse.API_KEY = ""  # enter your own API_KEY here

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

        # Send input message back to runtime
        communication_utils.sendMessageOverConnection(connection, input_message)

        # Decouple training conditions and uploading the sample
        upload_sample = False

        # Trigger the potential training image on condition
        if 'BBoxes_xyxy' in input_object and 'face' in input_object['BBoxes_xyxy'] and len(
                input_object['BBoxes_xyxy']['face']) < 4 * 4:
            print('Less than 4 faces detected')
            upload_sample = True

        # Upload the sample to Edge Impulse
        if upload_sample:
            # Parse image information
            image_header = msgpack.unpackb(image_header)

            # Read image
            image_data = communication_utils.read_shm(image_header["SHMKey"])
            with Image.frombytes("RGB", (image_header["Width"], image_header["Height"]), image_data) as image:
                with io.BytesIO() as output:
                    image.save(output, format="JPEG")
                    output.seek(0)
                    samples_buffer.append(output.getvalue())
            if len(samples_buffer) >= samples_buffer_flush_size:
                send_samples_buffer()


def signal_handler(sig, _):
    print("EXAMPLE PLUGIN: Received interrupt signal: ", sig)
    if len(samples_buffer) > 0:
        send_samples_buffer()
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
