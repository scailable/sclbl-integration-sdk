Postprocessor C Example
=========================

This example application provides an example on how to create a C based postprocessor that can be integrated with the NXAI Edge AI Manager.

# Postprocessors Control Flow

The normal control flow of a postprocessor is to receive a MessagePack binary message representing the inference results from the NXAI Edge AI Manager, and return the same or an altered version of the received MessagePack message.

An external postprocessor can parse the incoming MessagePack message, do analysis, optionally alter it, and return it. The alterations made by an external postprocessor will be kept and sent to the Network Optix server to be represented as bounding boxes or events.

An external postprocessor is a standalone application which is expected to receive these MessagePack messages and return a MessagePack message with a compatible format. Instructions can be added to a configuration file to handle executing and terminating the application.

Only one external processor is started for all devices. This means that a single processor can combine data for multiple devices for deeper analysis.

# MessagePack schema

The incoming MessagePack message follows a specific schema. If the message is altered, the returned message must follow the same schema. In Json, this schema would look like:

```json
{
    "DeviceID": "<Device ID>",
    "DeviceName": "<Device Name>",
    "Timestamp": <Timestamp>,
    "InputIndex": <Index>,
    "Width": <Width>,
    "Height": <Height>,
    "BBoxes_xyxy": {
        "<Class Name>": [<Float Coordinates>]
        },
    "ObjectsMetaData": {
        <"Class Name">: {
            "ObjectIDs": [
                <16-byte UUID>,
                <16-byte UUID>
            ],
            "AttributeKeys": [
                [<Attribute Key>,<Attribute Key>],
                [<Attribute Key>,<Attribute Key>]
            ],
            "AttributeValues": [
                [<Attribute Value>,<Attribute Value>],
                [<Attribute Value>,<Attribute Value>]
            ]
        }
    },
    "Scores": {
        <"Class Name"> : <Score>
    },
    "ExternalProcessorSettings": {}
}
 ```

Some fields depend on which model is assigned. If a model outputs bounding boxes, the `BBoxes_xyxy` field will be present. If a model outputs scores, the `Scores` field will be present.

# How to use

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
            "Command":"/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-c-example",
            "SocketPath":"/tmp/example-postprocessor.sock",
            "ReceiveInputTensor": false,
            "Objects": [
                {
                    "ID": "test",
                    "Name": "Test"
                }
            ]
        }
    ]
}
```

This tells the Edge AI Manager about the postprocessor:
- **Name** gives the postprocesor a name so it can be selected later
- **Command** defines how to start the postprocessor
- **SocketPath** tells the AI Manager where to send data to so the external postprocessor will receive it
- **ReceiveInputTensor** tells the AI Manager if this postprocessor expects information to access the raw input tensor data

The socket path is always given as the first command line argument when the application is started. It is therefore best practice for the external postprocessor application to read its socket path from here, instead of defining the data twice.

## Selecting to the postprocessor

If the postprocessor is defined correctly, its name should appear in the list of postprocessors in the NX Plugin settings. If it is selected in the plugin settings then the Edge AI Runtime will send data to the postprocessor and wait for its output.

# Licence

Copyright 2025, Network Optix, All rights reserved.