import os
import sys
import socket
import signal
import msgpack
import logging
import logging.handlers
import configparser

# Add the nxai-utilities python utilities
script_location = os.path.dirname(sys.argv[0])
sys.path.append(os.path.join(script_location, "../nxai-utilities/python-utilities"))
import communication_utils

CONFIG_FILE = os.path.join(script_location, "..", "etc", "plugin.image.pre.ini")

# Set up logging
if os.path.exists(os.path.join(script_location, "..", "etc")):
    LOG_FILE = os.path.join(script_location, "..", "etc", "plugin.image.pre.log")
else:
    LOG_FILE = os.path.join(script_location, "plugin.image.pre.log")

# Initialize plugin and logging, script makes use of INFO and DEBUG levels
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - example - %(message)s",
    filename=LOG_FILE,
    filemode="w",
)

# The socket this preprocessor will listen on.
# This is always given as the first argument when the process is started
# But it can be manually defined as well, as long as it is the same as the socket path in the runtime settings
Preprocessor_Socket_Path = "/tmp/example-image-preprocessor.sock"

# Define a single SHM object to share images back to AI Manager
global output_shm
output_shm = None


def parseImageFromSHM(shm_key: int, width: int, height: int, channels: int, external_settings: dict):
    global output_shm
    if output_shm is None:
        # Can reuse SHM ( if data is smaller or equal size ) or create new SHM and return ID
        input_image_size = width * height * channels
        output_shm = communication_utils.create_shm(input_image_size)
        print("EXAMPLE PLUGIN Created shm ID: ", output_shm.id, "Size:", output_shm.size)

    # Read image data from the shared memory
    image_data = communication_utils.read_shm(shm_key)

    # Check settings if image should be mirrored
    mirror_image = True
    if "externalprocessor.mirrorimage" in external_settings:
        mirror_image = external_settings["externalprocessor.mirrorimage"] == "true"

    if mirror_image is True:
        # Create new output image
        output_image = bytearray(len(image_data))
        new_width = int(width / 2)
        new_height = int(height / 2)
        # Mirror and downscale image
        for h_key in range(0, height, 2):
            for w_key in range(0, width, 2):
                output_pixel_index = int(((h_key * width / 4) * channels) + ((w_key / 2) * channels))
                input_pixel_index = (h_key * width * channels) + ((width - w_key) * channels)
                output_image[output_pixel_index : output_pixel_index + channels] = image_data[input_pixel_index : input_pixel_index + channels]
    else:
        # Return unmodified iamge
        output_image = image_data
        new_width = width
        new_height = height

    # Write un/modified image to shared memory
    communication_utils.write_shm(output_shm, output_image)

    return output_shm.id, new_width, new_height, channels


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

        external_settings = {}
        if "ExternalProcessorSettings" in image_header:
            logger.info("Got settings: " + str(image_header["ExternalProcessorSettings"]))
            external_settings = image_header["ExternalProcessorSettings"]

        # Process image
        output_shm_id, width, height, channels = parseImageFromSHM(
            image_header["SHMKey"],
            image_header["Width"],
            image_header["Height"],
            image_header["Channels"],
            external_settings,
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


def config():
    logger.info("Reading configuration from:" + CONFIG_FILE)

    try:
        configuration = configparser.ConfigParser()
        configuration.read(CONFIG_FILE)

        configured_log_level = configuration.get("common", "debug_level", fallback="INFO")
        set_log_level(configured_log_level)

        for section in configuration.sections():
            logger.info("config section: " + section)
            for key in configuration[section]:
                logger.info("config key: " + key + " = " + configuration[section][key])

    except Exception as e:
        logger.error(e, exc_info=True)

    logger.debug("Read configuration done")


def set_log_level(level):
    try:
        logger.setLevel(level)
    except Exception as e:
        logger.error(e, exc_info=True)


if __name__ == "__main__":
    print("EXAMPLE PREPROCESSOR: Input parameters: ", sys.argv)
    # Parse input arguments
    if len(sys.argv) > 1:
        Preprocessor_Socket_Path = sys.argv[1]
    # Handle interrupt signals
    signal.signal(signal.SIGTERM, signalHandler)

    ## initialize the logger
    logger = logging.getLogger(__name__)

    ## read configuration file if it's available
    config()

    logger.info("Initializing example plugin")
    logger.debug("Input parameters: " + str(sys.argv))

    try:
        main()
    except Exception as e:
        logger.error(e, exc_info=True)
    except KeyboardInterrupt:
        logger.info("Exited with keyboard interrupt")

    try:
        os.unlink(Preprocessor_Socket_Path)
    except OSError:
        if os.path.exists(Preprocessor_Socket_Path):
            logger.error("Could not remove socket file: " + Preprocessor_Socket_Path)
