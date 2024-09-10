NX Integration SDK
=========================

The NX Integration SDK provides tools and examples for clients to create applications which seamlessly integrates with the NX software stack.

See the subdirectories for further documentation.

## Requirements

### To Clone

The repository should be cloned with `--recurse-submodules`.

### To Compile

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

Also make sure that all of these are accessible from PATH.

### To run

These applications can be run on any platform on which they can be compiled.

## Getting Started

This project is CMake based, and all its modules can be compiled or gathered with CMake commands. To compile manually:

Create and enter build directory:

```shell
mkdir -p build && cd build
```

For the python postprocessors you need to set up a python virtual environment (especially needed on recent ubuntu servers) in the newly created build directory

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

## Install the postprocessors

Before installing make sure the target directory is writable.

```shell
sudo chmod 777 /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/
```

To install the generated postprocessor examples to the default postprocessors folder:

```shell
cmake --build . --target install
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
## Licence

Copyright 2024, Network Optix, All rights reserved.

## Directory structure

```
.
├── CMakeLists.txt
├── README.md
├── postprocessor-c-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── deps
│   │   ├── mpack.c
│   │   ├── mpack.h
│   │   └── nxai_data_utils.h
│   └── src
│       ├── main.c
│       └── nxai_data_utils.c
├── postprocessor-c-image-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── deps
│   │   ├── mpack.c
│   │   ├── mpack.h
│   │   └── nxai_data_utils.h
│   └── src
│       ├── main.c
│       └── nxai_data_utils.c
├── postprocessor-c-raw-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── deps
│   │   ├── mpack.c
│   │   ├── mpack.h
│   │   └── nxai_data_utils.h
│   └── src
│       ├── main.c
│       └── nxai_data_utils.c
├── postprocessor-cloud-inference-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── aws_utils.py
│   ├── postprocessor-cloud-inference-example.py
│   └── requirements.txt
├── postprocessor-python-edgeimpulse-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── postprocessor-python-edgeimpulse-example.py
│   └── requirements.txt
├── postprocessor-python-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── postprocessor-python-example.py
│   └── requirements.txt
├── postprocessor-python-image-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── postprocessor-python-image-example.py
│   └── requirements.txt
├── postprocessor-python-noresponse-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── postprocessor-python-noresponse-example.py
│   └── requirements.txt
└── sclbl-utilities
```
