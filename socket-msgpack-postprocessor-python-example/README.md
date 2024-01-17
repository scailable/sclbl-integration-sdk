Socket MessagePack Postprocessor Python Example
=========================

This example application provides an example on how to create a Python based postprocessor that can be integrated with the Scailable Edge AI Manager.

# MessagePack Postprocessors Control Flow

The normal control flow of a MessagePack postprocessor is to receive a MessagePack binary message representing the inference results from the Scailable Edge AI Manager, and return the same or an altered version of the received MessagePack message. This MessagePack message contains the output from the assigned model. 

An external postprocessor can parse the incoming MessagePack message, do analysis, optionally alter it, and return it. The alterations made by an external postprocessor will be kept and sent to the configured endpoint by the Edge AI Manager.

An external postprocessor is a standalone application which is expected to receive these MessagePack messages and return a similar MessagePack message. Instructions can be added to the Edge AI Manager settings file to handle executing and terminating the application.

# MessagePack schema

The incoming MessagePack message follows a specific schema. If the message is altered, the returned message must follow the same schema. In Json, this schema would look like:

```json
{
    "Outputs": {
        "<Output Name>": "<Binary data>",
        ....
    },
    "OutputRanks": "<Array of i32 values>",
    "OutputShapes": "<Array of arrays containing i64 values>",
    "OutptuDataTypes": "<Array of i32 values>"
}
```

Values can be added or removed from these fields, but the fields themselves are required.

The root level of the message is a MessagePack map with fields:
- "Outputs": A map containing the binary output tensors. The keys of the map are the names of the outputs, as defined in the model.
- "OutputRanks": An array of integer values indicating the dimensionality of the output's shape.
- "OutputShapes": An array of arrays containing the output shape of the tensor. The length of each inner array is equal to the dimensionality of the shape, as indicated by the corresponding output rank.
- "OutputDataTypes": An array of integer values, each indicating the type of the binary data contained in the "Outputs" field. The supported data types are as follows:

1. FLOAT
1. UINT8
1. INT8
1. UINT16
1. INT16
1. INT32
1. INT64
1. STRING
1. BOOL
1. DOUBLE
1. UINT32
1. UINT64

# How to use

Once compiled, copy the executable to an accessible directory. A convenience directory within the Edge AI Manager installation is created for this purpose at `/opt/sclbl/postprocessors`.

## Defining the postprocessor

Add the external postprocessor definition to the settings file at `/opt/sclbl/etc/settings.json` by adding the following object to the root object of the Json file:

``` json
"externalPostprocessors": [
    {
        "Name":"Python-Example-Postprocessor",
        "Command":"/opt/sclbl/postprocessors/postprocessor-python-example",
        "SocketPath":"/opt/sclbl/sockets/python-example-postprocessor.sock",
        "InputDataFormat":"MessagePack",
        "ReceiveInputTensor": 0
    }
]
```

This tells the Edge AI Manager about the postprocessor:
- **Name** gives the postprocesor a name so it can be routed to later
- **Command** defines how to start the postprocessor
- **SocketPath** tells the AI Manager where to send data to so the external postprocessor will receive it
- **InputDataFormat** tells the AI Manager that this postprocessor expects data in MessagePack format
- **ReceiveInputTensor** tells the AI Manager if this postprocessor expects information to access the raw input tensor data

The socket path is always given as the first command line argument when the application is started. It is therefore best practice for the external postprocessor application to read its socket path from here, instead of defining the data twice. A convience directory is created with the Edge AI Manager application is created for this purpose at `/opt/sclbl/sockets`.

## Routing to the postprocessor

Route a model to the external postprocessor by adding its name to the model's postprocessors:

```json
"module" :{
    "AssignedModels": [
        {
            "AssignedModelPostProcessors": ["Python-Example-Postprocessor"]
        }
    ]
}
```

Now each time this model is used for inference, its output will be sent to this postprocessor.


# Licence

Copyright 2023, Scailable, All rights reserved.