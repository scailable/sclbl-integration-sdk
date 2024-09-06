Edge Impulse Image Uploader
===========================

This example application uses a Python based postprocessor to upload images to Edge Impulse for training, either time based, or based on inference confidence.

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

Before building this postprocessor you need to enter your API key for the Edge Impulse Project.

Replace the key in `edge_impulse_api_key` with your own key, you can get your key in Edge Impulse Studio from the "Dashboard > Keys" page

In the python source file find the following line and update the `edge_impulse_api_key`

```python
# Add your own project level Edge Impulse API key
edge_impulse_api_key = "ei_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## Use the time based upload

When the `auto_generator` is set to `True` images will be uploaded according to the value in `auto_generator_every_seconds`

```python
# Option autogenerate images every x seconds as an alternative to sending based on p_value
auto_generator = True

# If auto_generator True, every how many seconds upload an image?
auto_generator_every_seconds = 1
```

## Use the confidence based upload

When the `auto_generator` is set to `False` images will be uploaded according to the value in `p_value`

```python
# Option autogenerate images every x seconds as an alternative to sending based on p_value
auto_generator = False

# ...

# Send images below this value to EdgeImpulse. Can be between 0.0 and 1.0
p_value = 0.4
```

## Preparation of dependencies

Install needed dependencies

```shell
sudo apt install cmake
sudo apt install g++
sudo apt install python3-pip
sudo apt install python3.12-venv
```

Change into the directory created for the project if you're not already there.

```shell
cd sclbl-integration-sdk/
```

Prepare the build directory, while in the project directory.

```shell
mkdir -p build
cd build
```

Set up a python virtual environment (needed on recent ubuntu servers) in the newly created build directory

```shell
python3 -m venv integrationsdk
source integrationsdk/bin/activate
```

## (optionally) Remove other postprocessors for compilation

Edit the `CMakelist.txt` to disable all but the external postprocessor

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

# Add Edge Impulse Postprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-python-edgeimpulse-example)

# Add installation option
install(TARGETS
    DESTINATION /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/
)
install(PROGRAMS
    ${CMAKE_CURRENT_BINARY_DIR}/postprocessor-python-edgeimpulse-example/postprocessor-python-edgeimpulse-example
    DESTINATION /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/
)
```

## Compile the postprocessor in python

Build and install the postprocessor, while in the project directory.

```shell
cmake ..
make
cmake --build . --target install
```

## Install the postprocessor

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
            "Command":"/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-python-edgeimpulse-example",
            "SocketPath":"/tmp/example-postprocessor.sock",
            "ReceiveInputTensor": 1,
            "RunLast": false,
            "NoResponse": true
        }
    ]
}
```

This tells the Edge AI Manager about the postprocessor:
- **Name** gives the postprocesor a name so it can be selected later
- **Command** defines how to start the postprocessor
- **SocketPath** tells the AI Manager where to send data to so the external postprocessor will receive it
- **ReceiveInputTensor** tells the AI Manager if this postprocessor expects information to access the raw input tensor data
- **Runlast** indicates when the postprocessor is run. When 'RunLast' is set to false, the external post-processor runs immediately after the model's inference. This means the raw data sent to the post-processor includes the output tensors' names, data, shapes, and data types. If 'RunLast' is set to true or left out, the external post-processor runs later, after the built-in post-processors. In this scenario, the data sent to the external post-processor is already processed, including output scores and bounding boxes (if applicable), scaled to match the original image dimensions rather than the model's processed image.
- **NoResponse** tells the AI Manager to not wait for a response from this postprocessor

The socket path is always given as the first command line argument when the application is started. It is therefore best practice for the external postprocessor application to read its socket path from here, instead of defining the data twice.

## Selecting to the postprocessor

If the postprocessor is defined correctly, its name should appear in the list of postprocessors in the NX Plugin settings. If it is selected in the plugin settings then the Edge AI Runtime will send data to the postprocessor and wait for its output.

## Output logging

There is an output log where the uploads can be tracked in real time from the server.

```shell
tail -f /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/etc/plugin.log
```

# Licence

Copyright 2024, Network Optix, All rights reserved.