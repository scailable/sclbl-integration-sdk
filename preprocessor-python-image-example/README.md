Socket MessagePack Preprocessor Python Image Example
=========================

This example application provides an example on how to create a Python based preprocessor that can be integrated with the NXAI Edge AI Manager.

This example reads an image from the AI Manager and will mirror the image horizontally. When this example is enabled, you should see the bounding boxes being mirrored with respect to the image.

# Preprocessors Control Flow

The normal control flow of a preprocessor is to receive a MessagePack binary message header from the AI Manager. This message will contain information on how to connect to a Shared Memory segment which contains the input image to the AI Manager.

The AI Manager will send the input image to the external postprocessors before following any of its own preprocessing steps, such as resizing and normalization. This allows for the external postprocessor to operate on the original image before the rest of the pipeline. 
For example, if an input stream to the AI Manager is YUV420, when RGB is required, a preprocessor could be added to intercept the original YUV420 image, and convert it to RGB instead.

The external preprocessor could write back an altered image to the shared memory segment sent by the AI Manager, or create a new shared memory segment and write a new image to the new segment. 

Finally, the external postprocessor sends back a message to the AI Manager, signalling that it's completed processing. This message contains the new or same shared memory ID, image width, height and channels. These could be the same or changed. The AI Manager will read the image from the shared memory segment ID sent back to the AI Manager, and use the received image width, height and channels in the rest of the pipeline.

# MessagePack schema

The header message sent to the external postprocessor contains information about the image and how to retrieve it through shared memory. In Json, this schema would look like:

```json
{
    "SHMKey": <Key>,
    "SHMID": <ID>,
    "Width": <Width>,
    "Height": <Height>,
    "Channels": <Channels>
}
```

The header message sent back to the AI Manager should contain all the same fields. The field values could be the same or changed.

# How to use

Once compiled, copy the executable to an accessible directory. A convenience directory within the Edge AI Manager installation is created for this purpose at `/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/preprocessors`.

It's a good idea to make sure the application and settings file you add is readable and executable by the NXAI Edge AI Manager. This can be achieved by running:

```
sudo chmod -R 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/preprocessors
```

## Defining the preprocessor

Create a configuration file at `/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/preprocessors/external_preprocessors.json` and add the details of your preprocessor to the root object of that file. For example: 

``` json
{
    "externalPreprocessors": [
        {
            "Name":"Example-Image-Preprocessor",
            "Command":"/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/preprocessors/preprocessor-python-image-example",
            "SocketPath":"/tmp/example-image-preprocessor.sock",
            "Schedule":"IMAGE",
            "Settings": [
                {
                    "type": "SwitchButton",
                    "name": "externalprocessor.mirrorimage",
                    "caption": "Mirror Image",
                    "description": "When this switch is active the input image to the AI Manager will be mirrored.",
                    "defaultValue": true
                }
            ]
        }
    ]
}
```

This tells the Edge AI Manager about the preprocessor:
- **Name** gives the preprocesor a name so it can be selected later
- **Command** defines how to start the preprocessor
- **SocketPath** tells the AI Manager where to send data to so the external preprocessor will receive it
- **Schedule** controls during which stage of the preprocessing pipeline the data is passed to the external processor. See #Schedules

The socket path is always given as the first command line argument when the application is started. It is therefore best practice for the external preprocessor application to read its socket path from here, instead of defining the data twice.

## Schedules

Schedules control during which stage of the processing pipeline the data will be passed to the external processor.

Available schedules are:

- **IMAGE**: The data will be passed to the external processor before any processing is done. The external processor will receive the raw image as it is received by the AI Manager. 
The returned image, if any, will then be resized, normalized, and cast to the specifications of the model.
- **TENSOR**: The data will be passed to the external processor after the image is processed. The external processor will receive a tensor structure containing the data of the processed image. 
The external processor has the option of adding/removing/renaming tensors which will be passed to the model.

## Selecting to the preprocessor

If the preprocessor is defined correctly, its name should appear in the list of preprocessors in the NX Plugin settings. If it is selected in the plugin settings then the Edge AI Runtime will send data to the preprocessor and wait for its output.

# Licence

Copyright 2024, Network Optix, All rights reserved.