import os
import sys
import socket
import signal
import msgpack

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
Postprocessor_Socket_Path = "/opt/sclbl/sockets/python-example-postprocessor.sock"


def main():
    # Validate running state
    status = communication_utils.getScailableStatus()
    if status["Running"] == False:
        print(
            "EXAMPLE PLUGIN: Postprocessor started without the Scailable Runtime running. This will probably not work."
        )
    # Validate settings
    validateSettings()

    # Start socket listener to receive messages from Scailable runtime
    server = communication_utils.startUnixSocketServer(Postprocessor_Socket_Path)
    # Wait for messages in a loop
    while True:
        # Wait for input message from runtime
        try:
            input_message, connection = communication_utils.waitForSocketMessage(server)
        except socket.timeout:
            # Request timed out. Continue waiting
            continue

        print("EXAMPLE PLUGIN: Received input message: ", input_message)

        # Parse input message
        input_object = msgpack.unpackb(input_message)

        print("Unpacked ", input_object)

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

        # Add extra output
        input_object["Outputs"][
            "Python-MsgPack-Socket-Postprocessor"
        ] = "Processed".encode()
        input_object["OutputRanks"].append(1)
        input_object["OutputShapes"].append([9])
        input_object["OutputDataTypes"].append(8)

        print("Packing ", input_object)

        # Write object back to string
        output_message = msgpack.packb(input_object, use_bin_type=True)

        # Send message back to runtime
        communication_utils.sendMessageOverConnection(connection, output_message)


def validateSettings():
    settings = communication_utils.getScailableSettings()
    # Validate postprocessor is defined in 'externalPostprocessors' setting
    external_postprocessors = []
    if "externalPostprocessors" in settings:
        external_postprocessors = settings["externalPostprocessors"]
    for postprocessor in external_postprocessors:
        if postprocessor["Name"] == Postprocessor_Name:
            break
    else:
        print(
            "EXAMPLE PLUGIN: Postprocessor started without being defined in 'externalPostprocessors' setting. This will probably not work"
        )
    # Validate postprocessor is assigned to a model
    is_assigned = False
    for model_data in settings["module"]["AssignedModels"]:
        for assigned_postprocessor in model_data["AssignedModelPostProcessors"]:
            if assigned_postprocessor == Postprocessor_Name:
                is_assigned = True
    if is_assigned == False:
        print(
            "EXAMPLE PLUGIN: Postprocessor started without being assigned to any model. This will probably not work"
        )


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
