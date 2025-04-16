Postprocessor Python Setting Example
============================

This example application provides an example on how to create a Python based postprocessor that can be integrated with the NXAI Edge AI Manager.

This plugin defines its settings in its definition in `external_postprocessors.json`. These settings then appear in the plugin UI and will be passed through to the external postprocessor.

# Postprocessors Control Flow

The normal control flow of a postprocessor is to receive a MessagePack binary message representing the inference results from the NXAI Edge AI Manager, and return the same or an altered version of the received MessagePack message.

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
    },
    "ExternalProcessorSettings": {
        <"Setting Key"> : <"Setting Value">
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

# Requirements

For this example to work, you can use any model.

# How to use

## Download the integration SDK

You probably have the integration SDK already if you're looking at this readme, the command to get the full integration SDK is as follows:

```shell
git clone https://github.com/scailable/sclbl-integration-sdk.git --recurse-submodules
```

If you have downloaded the sdk previously, you can also update to the latest version of the integration SDK while in the directory of the downloaded git repository.

```shell
git pull --recurse-submodules
```

## Configuration of example postprocessor

Create a [configuration file](plugin.example.ini.example) at `/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/etc/plugin.example.ini` and add some overrides for the configuration.

This plugin only supports changing the debug level between DEBUG, INFO, WARNING, ERROR and CRITICAL

For example:

```ini
[common]
debug_level=DEBUG
```

## Preparation of dependencies

Install the needed dependencies

```shell
sudo apt install cmake
sudo apt install g++
sudo apt install python3-pip
sudo apt install patchelf
```

Change into the directory created for the project if you're not already there.

```shell
cd sclbl-integration-sdk/
```

Prepare the *build* directory in the project directory, and switch to the build directory.

```shell
mkdir -p build
cd build
```

Set up a python virtual environment in the newly created build directory (on recent ubuntu servers this is required).

```shell
python3 -m venv integrationsdk
source integrationsdk/bin/activate
```

## (optionally) Remove other postprocessors for compilation

Edit the `CMakelist.txt` to disable all but the external postprocessor.

```shell
nano ../CMakeLists.txt
```

It should look similar to this

```shell
cmake_minimum_required(VERSION 3.10.2)

project(sclbl-integration-examples)

# Add Scailable C Utilities for all subprojects
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/sclbl-utilities)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/sclbl-utilities/include)

# Add Settings Postprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-python-settings-example)

# Add installation option
install(TARGETS
    DESTINATION /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/
)
install(PROGRAMS
    ${CMAKE_CURRENT_BINARY_DIR}/postprocessor-python-settings-example/postprocessor-python-settings-example
    DESTINATION /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/
)
```

## Compile the postprocessor

Build the postprocessor, while in the created *build* directory. This may take a while, depending on the speed of your system.

```shell
cmake ..
make
```

## Install the postprocessor

Once compiled, copy the executable to an accessible directory.

A convenience directory within the Edge AI Manager installation is created for this purpose at `/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors`.

The application and settings files you add must be readable and executable by the NX AI Edge AI Manager. This can be achieved by running:

```
sudo chmod -R 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors
```

Install the postprocessor automatically with the cmake command, also from within the *build* directory.

```shell
cmake --build . --target install
```

## Defining the postprocessor

Create a configuration file at `/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/external_postprocessors.json` and add the details of your postprocessor to the root object of that file.

For example:

``` json
{
    "externalPostprocessors": [
        {
            "Name":"Example-Postprocessor-Setting",
            "Command":"/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-python-settings-example",
            "SocketPath":"/tmp/python-example-settings-postprocessor.sock",
            "ReceiveInputTensor": false,
            "ReceiveConfidenceData": false,
            "Settings": [
                {
                    "type": "TextField",
                    "name": "externalprocessor.attributeName",
                    "caption": "Attribute Name",
                    "description": "The name of the example attribute",
                    "defaultValue": "Key"
                },
                {
                    "type": "TextField",
                    "name": "externalprocessor.attributeValue",
                    "caption": "Attribute Value",
                    "description": "The value of the example attribute",
                    "defaultValue": "Value"
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
- **Settings** defines the settings which will appear in the plugin UI.

The socket path is always given as the first command line argument when the application is started. It is therefore best practice for the external postprocessor application to read its socket path from here, instead of defining the data twice.

## Defining the settings

The settings should be defined as in the schema from the NetworkOptix Metadata SDK, as documented in `settings_model.md` ( included in this directory as an example ).

The settings will always be sent to the external postrprocessor as a string representation, this includes integers and floats. It will be up to the external postprocessor to correctly convert these values to usable types.

The `"name"` value in the settings should always start with `externalprocessor.`, otherwise they will be ignored. 
For performance reasons, settings aren't sorted per external postprocessor. This means that if you have multiple external postprocessors each with their own settings, then each postprocessor will receive all settings for all postprocessors.

## Restarting the server

Finally, to (re)load your new postprocessor, make sure to restart the NX Server with:

```shell
sudo service networkoptix-metavms-mediaserver restart
```

You also want to make sure the postprocessor can be used by the NX AI Manager (this is the mostly same command as earlier)

```shell
sudo chmod -R a+x /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/
```

## Selecting to the postprocessor

If the postprocessor is defined correctly, its name should appear in the list of postprocessors in the NX Plugin settings. If it is selected in the plugin settings then the Edge AI Runtime will send data to the postprocessor and wait for its output.

## Output logging

There is an output log where the uploads can be tracked in real time from the server.

```shell
tail -f /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/etc/plugin.settings.log
```

# Licence

Copyright 2025, Network Optix, All rights reserved.