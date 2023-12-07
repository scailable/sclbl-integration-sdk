Socket Json Postprocessor Python Example
=========================

This example application provides an example on how to create a Python based postprocessor that can be integrated with the Scailable Edge AI Manager.

# Json Postprocessors Control Flow

The normal control flow of a Json postprocessor is to receive a Json string representing the inference results from the Scailable Edge AI Manager, and return the same or an altered version of the received Json string. This json string contains the output from the assigned model, along with metadata added by the Scailable Edge AI Manager, and optionall added data from assigned postprocessors inside the Edge AI Manager. 

An external postprocessor can parse the incoming Json string, do analysis, optionally alter it, and return it. The alterations made by an external postprocessor will be kept and sent to the configured endpoint by the Edge AI Manager.

An external postprocessor is a standalone application which is expected to receive these Json strings and return a similar Json string. Instructions can be added to the Edge AI Manager settings file to handle executing and terminating the application.

# How to use

Once compiled, copy the executable to an accessible directory. A convenience directory within the Edge AI Manager installation is created for this purpose at `/opt/sclbl/postprocessors`.

## Defining the postprocessor

Add the external postprocessor definition to the settings file at `/opt/sclbl/etc/settings.json` by adding the following object to the root object of the Json file:

``` json
"externalPostprocessors": [
    {
        "Name":"Python-Example-Postprocessor",
        "Command":"/opt/sclbl/postprocessors/postprocessor-python-example",
        "SocketPath":"/opt/sclbl/sockets/python-example-postprocessor.sock"
    }
]
```

This tells the Edge AI Manager about the postprocessor:
- **Name** gives the postprocesor a name so it can be routed to later
- **Command** defines how to start the postprocessor
- **SocketPath** tells the AI Manager where to send data to so the external postprocessor will receive it

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