import os
import sys
import socket
import signal
import uuid

# Add the sclbl-utilities python utilities
script_location = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(script_location, "../sclbl-utilities/python-utilities"))
import communication_utils

# The name of the postprocessor.
# This is used to match the definition of the postprocessor with routing.
Postprocessor_Name = "Example-Tracker-Postprocessor"

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

bboxes_cache = {}


def calculateIOU(boxA, boxB):
    # Calculate the Intersection Over Union (IOU) of boxA and boxB
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou


def trackObjects(input_object) -> dict:
    device_id = input_object["DeviceID"]
    if device_id not in bboxes_cache:
        bboxes_cache[device_id] = {}
    cached_device_bboxes = bboxes_cache[device_id]

    # Tracking is done per class
    bboxes_ids = {}
    for class_name in input_object["BBoxes_xyxy"]:
        if class_name not in cached_device_bboxes:
            cached_device_bboxes[class_name] = {"BBoxes": [], "IDs": []}
        cached_class_bboxes = cached_device_bboxes[class_name]["BBoxes"]
        cached_class_ids = cached_device_bboxes[class_name]["IDs"]
        new_class_bboxes = input_object["BBoxes_xyxy"][class_name]
        comparisons = []
        for new_index in range(int(len(new_class_bboxes) / 4)):
            for old_index in range(int(len(cached_class_bboxes) / 4)):
                overlap = calculateIOU(
                    cached_class_bboxes[old_index * 4 : (old_index * 4) + 4],
                    new_class_bboxes[new_index * 4 : (new_index * 4) + 4],
                )
                comparisons.append((overlap, old_index, new_index))
        # Sort bboxes according to overlap
        comparisons.sort(key=lambda x: x[0])
        # Match new boxes to cached boxes
        cached_matched = [False] * len(cached_class_bboxes)
        new_matched = [False] * len(new_class_bboxes)
        bboxes_ids[class_name] = [None] * int(len(new_class_bboxes) / 4)
        for comparison in comparisons:
            if (
                comparison[0] > 0
                and cached_matched[comparison[1]] == False
                and new_matched[comparison[2]] == False
            ):
                cached_matched[comparison[1]] = True
                new_matched[comparison[2]] = True
                # Update cached box to new box
                cached_class_bboxes[comparison[1] * 4 : (comparison[1] * 4) + 4] = (
                    new_class_bboxes[comparison[2] * 4 : (comparison[2] * 4) + 4]
                )
                # Record old ID
                bboxes_ids[class_name][comparison[2]] = cached_class_ids[comparison[1]]
        # For all unmatched objects, generate new ID
        for id_index in range(len(bboxes_ids[class_name])):
            if bboxes_ids[class_name][id_index] is None:
                # Generate new ID
                bboxes_ids[class_name][id_index] = uuid.uuid4().bytes
                # Add box to cache
                cached_class_bboxes.extend(
                    new_class_bboxes[id_index * 4 : (id_index * 4) + 4]
                )
                cached_class_ids.append(bboxes_ids[class_name][id_index])
    return bboxes_ids


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

        # Parse input message
        input_object = communication_utils.parseInferenceResults(input_message)

        print("Unpacked ", input_object)

        input_object["ObjectIDs"] = trackObjects(input_object)

        print("Packing ", input_object)

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
