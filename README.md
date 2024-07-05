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

- sudo apt install cmake
- sudo apt install g++

Also make sure that all of these are accessible from PATH.

### To run

These applications can be run on any platform on which they can be compiled.


## Getting Started

This project is CMake based, and all its modules can be compiled or gathered with CMake commands. To compile manually:

Create and enter build directory:

```
mkdir build && cd build
```

Set up CMake configuration:

```
cmake ..
```

Build all targets:

```
make
```

This will build the default target, which includes the all the example applications.

To install the generated postprocessor examples to the default postprocessors folder:

```
cmake --build . --target install
```

## Licence

Copyright 2024, Network Optix, All rights reserved.

## Directory structure

```
.
├── CMakeLists.txt
├── nxai-utilities
│   ├── CMakeLists.txt
│   ├── include
│   │   ├── musl_time.h
│   │   ├── nxai_data_structures.h
│   │   ├── nxai_process_utils.h
│   │   ├── nxai_shm_utils.h
│   │   └── nxai_socket_utils.h
│   ├── python-utilities
│   │   ├── communication_utils.py
│   │   └── requirements.txt
│   ├── README.md
│   └── src
│       ├── nxai_process_utils.c
│       ├── nxai_shm_utils.c
│       └── nxai_socket_utils.c
├── postprocessor-c-example
│   ├── CMakeLists.txt
│   ├── deps
│   │   ├── mpack.c
│   │   ├── mpack.h
│   │   └── nxai_data_utils.h
│   ├── README.md
│   └── src
│       ├── main.c
│       └── nxai_data_utils.c
├── postprocessor-c-image-example
│   ├── CMakeLists.txt
│   ├── deps
│   │   ├── mpack.c
│   │   ├── mpack.h
│   │   └── nxai_data_utils.h
│   ├── README.md
│   └── src
│       ├── main.c
│       └── nxai_data_utils.c
├── postprocessor-cloud-inference-example
│   ├── aws_utils.py
│   ├── CMakeLists.txt
│   ├── postprocessor-cloud-inference-example.py
│   ├── README.md
│   └── requirements.txt
├── postprocessor-c-raw-example
│   ├── CMakeLists.txt
│   ├── deps
│   │   ├── mpack.c
│   │   ├── mpack.h
│   │   └── nxai_data_utils.h
│   ├── README.md
│   └── src
│       ├── main.c
│       └── nxai_data_utils.c
├── postprocessor-python-edgeimpulse-example
│   ├── CMakeLists.txt
│   ├── postprocessor-python-edgeimpulse-example.py
│   ├── README.md
│   └── requirements.txt
├── postprocessor-python-example
│   ├── CMakeLists.txt
│   ├── postprocessor-python-example.py
│   ├── README.md
│   └── requirements.txt
├── postprocessor-python-image-example
│   ├── CMakeLists.txt
│   ├── postprocessor-python-image-example.py
│   ├── README.md
│   └── requirements.txt
├── postprocessor-python-noresponse-example
│   ├── CMakeLists.txt
│   ├── postprocessor-python-noresponse-example.py
│   ├── README.md
│   └── requirements.txt
├── postprocessor-python-tracker-example
│   ├── CMakeLists.txt
│   ├── postprocessor-python-tracker-example.py
│   ├── README.md
│   └── requirements.txt
├── README.md
```
