Cloud inference with the Nx AI Manager
=========================

> Before delving into this example, please review the [Python example](../postprocessor-python-image-example/) to understand how to configure the post-processing

# Overview

This example is meant to be used to illustrate how the Nx AI Manager allows the user to perform additional data analysis on the stream logic on a cloud machine.   
For the sake of example, the AWS Rekognition API was used to perform age, gender and emotion classification on faces detected by the AI Manager.

The workflow is as follows:
1. The AI Manager runs a face detection model on each frame
2. When the model inference is accomplished, the AI Manager sends its output to the Python external post-processor that sends a request (per detected face) to AWS Rekognition, and waits for response.
3. The post-processor overwrites the category of the detected object (ie. "face") to a more insightful one, such as: "A male in his 30s feeling happy", and sends back the result to Nx to visualize it.

## Requirements

For this example to work, you need to ensure that you have assigned the Face locator model on your edge device from the Nx AI Cloud.   
Additionally, you need to set your AWS credential keys in the [aws_utils.py](aws_utils.py) file.
```python
session = boto3.Session(
    aws_access_key_id='',  # Specify your access key
    aws_secret_access_key='', # Specify your secret key
    region_name='us-east-1'  # Specify your region
)
```

# How To Use

Once compiled, copy the executable to an accessible directory. A convenience directory within the Edge AI Manager installation is created for this purpose at `/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors`.

It's a good idea to make sure the application and settings file you add is readable and executable by the NXAI Edge AI Manager. This can be achieved by running:

```
sudo chmod -R 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors
```

## Defining the postprocessor

Create a configuration file at `/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/external_postprocessors.json` and add the details of your postprocessor to the root object of that file. For example: 

``` json
{
    "externalPostprocessors": [
        {
            "Name":"Example-Postprocessor",
            "Command":"/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-cloud-inference-example",
            "SocketPath":"/tmp/example-postprocessor.sock",
            "ReceiveInputTensor": 1
        }
    ]
}
```

This tells the Edge AI Manager about the postprocessor:
- **Name** gives the postprocesor a name so it can be selected later
- **Command** defines how to start the postprocessor
- **SocketPath** tells the AI Manager where to send data to so the external postprocessor will receive it
- **ReceiveInputTensor** tells the AI Manager if this postprocessor expects information to access the raw input tensor data

# Licence

Copyright 2024, Network Optix, All rights reserved.