Postprocessor C Image Example
=========================

This example application provides an example on how to create a C based postprocessor that can be integrated with the NXAI Edge AI Manager.

# Postprocessors Control Flow

The normal control flow of a postprocessor is to receive a MessagePack binary message representing the inference results from the NXAI Edge AI Manager, and return the same or an altered version of the received MessagePack message.

This example will show how to access the input tensor which the inference results were generated from for additional analysis or presentation. It is possible to define the postprocessor indicating that the Edge AI Runtime should send additional information to allow the postprocessor to access the input tensor. If this setting is enabled, the Edge AI Manager will send an additional messagePack message after the inference results messages containing the relevant fields. The postprocessor should therefore expect two messages before responding.

An external postprocessor can parse the incoming MessagePack message, do analysis, optionally alter it, and return it. The alterations made by an external postprocessor will be kept and sent to the Network Optix server to be represented as bounding boxes or events.

An external postprocessor is a standalone application which is expected to receive these MessagePack messages and return a MessagePack message with a compatible format. Instructions can be added to a configuration file to handle executing and terminating the application.

# MessagePack schema

The incoming MessagePack message follows a specific schema. If the message is altered, the returned message must follow the same schema. In Json, this schema would look like:

```json
{
    "Timestamp": <Timestamp>,
    "Width": <Width>,
    "Height": <Height>,
    "InputIndex": <Index>,
    "Counts": {
        <"Class Name">: <Class Count>
    },
    "BBoxes_xyxy": {
        <"Class Name">: [
            <Coordinates>
        ]
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
    }
}
```

The image header message contains fields indicating information about the image dimensions and information to access this data:

```json
{
    "Width": <Width>,
    "Height": <Height>,
    "SHMKey": <SHM Key>,
    "SHMID": <SHM ID>
}
```

A convenience example function is provided showing how to use this data to access the original tensor data in shared memory.

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
            "Command":"/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-c-image-example",
            "SocketPath":"/tmp/example-c-image-postprocessor.sock",
            "ReceiveInputTensor": true
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