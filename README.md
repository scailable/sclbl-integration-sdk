Scailable Integration SDK
=========================

The Scailable Integration SDK provides tools and examples for clients to create applications which seamlessly integrates with the Scailable software stack.

See the subdirectories for further documentation.

## Requirements

### To Compile

These applications can be compiled on any architecture natively in a Linux environment.

To compile, some software packages are required. These can be installed by running:

- cmake
- g++

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

Build all target:

```
make
```

This will build the default target, which includes the all the example applications.

To install the generated postprocessor examples to the default postprocessors folder:

```
cmake --build . --target install
```

## Licence

Copyright 2022, Scailable, All rights reserved.

## Directory structure

```
├── CMakeLists.txt
├── README.md
├── sclbl-utilities
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── include
│   │   └── sclbl_socket_utils.h
│   ├── python-utilities
│   │   └── communication_utils.py
│   └── src
│       └── sclbl_socket_utils.c
├── socket-json-postprocessor-c-example
│   ├── CMakeLists.txt
│   ├── deps
│   │   ├── yyjson.c
│   │   └── yyjson.h
│   └── src
│       └── main.c
└── socket-json-postprocessor-python-example
    ├── CMakeLists.txt
    ├── postprocessor-python-example.py
    ├── postprocessor-python-example.spec
    └── requirements.txt
```