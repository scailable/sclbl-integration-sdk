NX Integration SDK
==================

The NX Integration SDK provides tools and examples for clients to create applications which seamlessly integrates with the NX software stack.

See the subdirectories for further documentation.

# Requirements

## Download the integration SDK

You probably have the integration SDK already if you're looking at this readme, the command to get the full integration SDK is as follows:

```shell
git clone https://github.com/scailable/sclbl-integration-sdk.git --recurse-submodules
```

If you have downloaded the sdk previously, you can also update to the latest version of the integration SDK while in the directory of the downloaded git repository.

```shell
git pull --recurse-submodules
```

The repository should be cloned with `--recurse-submodules`.

## Requirements to compile the postprocessors

These applications can be compiled on any architecture natively in a Linux environment.

To compile, some software packages are required. These can be installed by running:

```shell
sudo apt install cmake
sudo apt install g++
```

For the python postprocessors the following is also required

```shell
sudo apt install python3-pip
sudo apt install python3.12-venv
```

## Requirements to run the postprocessors

These applications can be run on any platform on which they can be compiled.

# How to use

## Getting Started

This project is CMake based, and all its modules can be compiled or gathered with CMake commands.

Because the different postprocessors must be compiled for each hardware architecture this repository does not include pre-built binaries. All processors can be compiled manually.

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

Set up CMake configuration:

```shell
cmake ..
```

Build all targets:

```shell
make
```

This will build the default target, which includes the all the example applications that are active in the `CMakeLists.txt`.

It is possible to only run specific examples, refer to the readme files in the subdirectories of those examples for specific instructions.

## Install the postprocessors

Before installing make sure the target directory is writable.

```shell
sudo chmod 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/
```

To install the generated postprocessor examples to the default postprocessors folder:

```shell
cmake --build . --target install
```

## Defining the postprocessor

Create a configuration file at `/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/external_postprocessors.json` and add the details of your postprocessors to the root object of that file. For example the following file enables *all* python based postprocessors:

```json
{
    "externalPostprocessors": [
        {
            "Name":"EI-Upload-Postprocessor",
            "Command":"/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-python-edgeimpulse-example",
            "SocketPath":"/tmp/python-edgeimpulse-postprocessor.sock",
            "ReceiveInputTensor": 1,
            "RunLast": false,
            "NoResponse": true
        },
        {
            "Name":"Example-Postprocessor",
            "Command":"/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-python-example",
            "SocketPath":"/tmp/python-example-postprocessor.sock",
            "ReceiveInputTensor": 0
        },
        {
            "Name":"Image-Postprocessor",
            "Command":"/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-python-image-example",
            "SocketPath":"/tmp/python-image-postprocessor.sock",
            "ReceiveInputTensor": 1
        },
        {
            "Name":"NoResponse-Postprocessor",
            "Command":"/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-python-noresponse-example",
            "SocketPath":"/tmp/python-noresponse-postprocessor.sock",
            "ReceiveInputTensor": 0,
            "ReceiveBinaryData": false,
            "NoResponse": true
        },
        {
            "Name":"Cloud-Inference-Postprocessor",
            "Command":"/opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/postprocessor-cloud-inference-example",
            "SocketPath":"/tmp/python-cloud-inference-postprocessor.sock",
            "ReceiveInputTensor": 1
        }

    ]
}
```

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

# Directory structure

```
.
├── CMakeLists.txt
├── README.md
├── postprocessor-c-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── deps
│   │   ├── mpack.c
│   │   ├── mpack.h
│   │   └── nxai_data_utils.h
│   └── src
│       ├── main.c
│       └── nxai_data_utils.c
├── postprocessor-c-image-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── deps
│   │   ├── mpack.c
│   │   ├── mpack.h
│   │   └── nxai_data_utils.h
│   └── src
│       ├── main.c
│       └── nxai_data_utils.c
├── postprocessor-c-raw-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── deps
│   │   ├── mpack.c
│   │   ├── mpack.h
│   │   └── nxai_data_utils.h
│   └── src
│       ├── main.c
│       └── nxai_data_utils.c
├── postprocessor-cloud-inference-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── aws_utils.py
│   ├── postprocessor-cloud-inference-example.py
│   └── requirements.txt
├── postprocessor-python-edgeimpulse-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── postprocessor-python-edgeimpulse-example.py
│   └── requirements.txt
├── postprocessor-python-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── postprocessor-python-example.py
│   └── requirements.txt
├── postprocessor-python-image-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── postprocessor-python-image-example.py
│   └── requirements.txt
├── postprocessor-python-noresponse-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── postprocessor-python-noresponse-example.py
│   └── requirements.txt
└── sclbl-utilities
```

# Licence

Copyright 2024, Network Optix, All rights reserved.