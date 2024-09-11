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

You also need an AWS account and the associated Access Key and Access Secret.

# How To Use

Once compiled, copy the executable to an accessible directory. A convenience directory within the Edge AI Manager installation is created for this purpose at `/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors`.

It's a good idea to make sure the application and settings file you add is readable and executable by the NXAI Edge AI Manager. This can be achieved by running:

```
sudo chmod -R 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors
```

## Local configuration

You need to set your AWS credential keys in the configuration file at `~/.aws/credentials`:

```ini
[default]
aws_access_key_id=acced_key
aws_secret_access_key=secret_access_key
```

You can configure other settings in the configuration file at `/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/etc/plugin.cloud-inference.ini`:

```ini
[common]
debug_level=DEBUG
[inference]
image_path=/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/face.png
```

## Defining the postprocessor

Create a configuration file at `/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/external_postprocessors.json` and add the details of your postprocessor to the root object of that file. For example: 

``` json
{
    "externalPostprocessors": [
        {
            "Name":"Cloud-Inference-Postprocessor",
            "Command":"/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-cloud-inference-example",
            "SocketPath":"/tmp/python-cloud-inference-postprocessor.sock",
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

## Restarting the server

Finally, to (re)load your new postprocessor, make sure to restart the NX Server with:

```shell
sudo service networkoptix-metavms-mediaserver restart
```

You also want to make sure the postprocessor can be used by the NX AI Manager (this is the mostly same command as earlier)

```
sudo chmod -R a+x /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/
```

## Selecting to the postprocessor

If the postprocessor is defined correctly, its name should appear in the list of postprocessors in the NX Plugin settings. If it is selected in the plugin settings then the Edge AI Runtime will send data to the postprocessor and wait for its output.

# Licence

Copyright 2024, Network Optix, All rights reserved.