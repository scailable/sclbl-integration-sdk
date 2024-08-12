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
# noinspection PyUnresolvedReferences
from PIL import Image
# noinspection PyUnresolvedReferences
import edgeimpulse


# Set up logging
LOG_FILE = ("/opt/networkoptix-metavms/mediaserver/bin/plugins/"
            "nxai_plugin/nxai_manager/etc/plugin.log")
			
# Add your own project level Edge Impulse API key	
edge_impulse_api_key = "ei_ac02e87882ebf271af5d5cd6e2182354e6cb44a8b597e894"

# Option autogenerate images every x seconds as an alternative to sending based on p_value
auto_generator = False

# If auto_generator True, every how many seconds upload an image?
auto_generator_every_seconds = 1

# We keep a counter to generate unique filenames.
samples_counter: int = 0

# The buffer with samples to batch.
samples_buffer: list = []

# Flush the buffer at this length
samples_buffer_flush_size = 20

# Send images below this value to EdgeImpulse. Can be between 0.0 and 1.0
p_value = 0.4

# Initialize plugin and logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=LOG_FILE, filemode="w")
logging.debug("Initializing plugin")


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
        logging.info("Sending {c} samples to Edge Impulse...".format(c=len(samples_buffer)))
        start_at = time.perf_counter()
        samples = []
        for contents in samples_buffer:
            samples_counter += 1
            logging.info("Create sample" + str(samples_counter))
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

        logging.info("Done creating samples, starting upload...")
        response = edgeimpulse.experimental.data.upload_samples(samples)
        logging.info("Done upload")

        # Check to make sure there were no failures
        if (len(response.fails)) != 0:
            logging.info("Could not upload files")

        end_at = time.perf_counter()
        logging.info("Send {c} samples in {d:0.1f}sec to Edge Impulse. Total {t}".format(
            c=len(samples_buffer), d=end_at-start_at, t=samples_counter,
        ))
        logging.info("Send a total of {t} samples to Edge Impulse".format(t=samples_counter))

        samples_buffer = []
    else:
        logging.info("No samples to send to Edge Impulse. Total {t}".format(t=samples_counter))


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

    global samples_buffer
    global samples_counter
    global p_value
    global auto_generator
    global auto_generator_every_seconds
	global edge_impulse_api_key

    # Add your own project level Edge Impulse API key
    edgeimpulse.API_KEY = edge_impulse_api_key

    # Start socket listener to receive messages from NXAI runtime
    try:
        os.remove(Postprocessor_Socket_Path)
    except OSError:
        pass
    server = communication_utils.startUnixSocketServer(Postprocessor_Socket_Path)
    # Wait for messages in a loop

    counter = 0

    # Get the current time at the start
    start_time = time.time()

    while True:

        upload_sample = False

        counter = counter + 1

        logging.debug("Wait for message " + str(counter))
        # Wait for input message from runtime
        try:
            input_message, connection = communication_utils.waitForSocketMessage(server)
            image_header = communication_utils.receiveMessageOverConnection(connection)
        except socket.timeout:
            # Request timed out. Continue waiting
            continue

        logging.debug("Message " + str(counter) + "received")

        # Parse input message
        parsed_response = msgpack.unpackb(input_message)

        # Read Output types, shapes and sizes
        output_data_types = parsed_response.get("OutputDataTypes")  # 1 for float32 and 3 for int8
        output_shapes = parsed_response.get("OutputShapes")
        output_sizes = [prod(output_shapes[i]) for i in range(len(output_shapes))]

        # Unpack Output values
        for i, key in enumerate(parsed_response["Outputs"]):
            value = parsed_response["Outputs"][key]
            if output_data_types[i] == 1:
                parsed_response["Outputs"][key] = list(
                    struct.unpack("f" * output_sizes[i], value)
                )
            elif output_data_types[i] == 3:
                parsed_response["Outputs"][key] = list(
                    struct.unpack("b" * output_sizes[i], value)
                )

        logging.debug("Message " + str(counter) + " parsed")

        # Use pformat to format the deep object
        formatted_object = pformat(parsed_response)
        logging.debug(f'Parsed response:\n\n{formatted_object}\n\n')

        current_time = time.time()

        # Check if auto_generator is True and 60 seconds have passed
        if auto_generator and current_time - start_time >= auto_generator_every_seconds:

            start_time = current_time
            logging.info("Add timed sample (every )" + str(auto_generator_every_seconds)
                         + "(seconds) number " + str(counter) + " to upload queue")
            upload_sample = True

        elif not auto_generator:

            # Retrieve the bounding box values
            bbox_values = parsed_response['Outputs']['bboxes-format:xyxysc;0:class0;1:class1']

            # Number of elements in each bounding box entry (assuming format: x1, y1, x2, y2, score, class)
            num_elements_per_entry = 6

            # Extract every 5th out of six values
            parsed_values = [bbox_values[i] for i in range(4, len(bbox_values), num_elements_per_entry)]

            # Check if any of the values are below p_value and earmark result for retrieval
            for value in parsed_values:
                if value < p_value:
                    logging.debug("Parsed value: %.8f", value)
                    upload_sample = True

        if upload_sample:
            logging.info("x")
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
        else:
            logging.info(".")

        # Create msgpack formatted message
        data_types = parsed_response.get("OutputDataTypes")
        for key in parsed_response['Outputs']:
            value = parsed_response['Outputs'][key]
            if data_types[0] == 1:
                parsed_response['Outputs'][key] = struct.pack("f" * len(value), *value)
            elif data_types[0] == 3:
                parsed_response['Outputs'][key] = struct.pack("b" * len(value), *value)
        message_bytes = msgpack.packb(parsed_response)

        # Send message back to runtime
        communication_utils.sendMessageOverConnection(connection, message_bytes)


def signalHandler(sig, _):
    logging.debug("EXAMPLE PLUGIN: Received interrupt signal: " + str(sig))
    if len(samples_buffer) > 0:
        send_samples_buffer()
    sys.exit(0)


if __name__ == "__main__":
    logging.debug("EXAMPLE PLUGIN: Input parameters: " + str(sys.argv))
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
