NX Integration SDK
=========================

The NX Integration SDK provides tools and examples for clients to create applications which seamlessly integrates with the NX software stack.

See the subdirectories for further documentation.

## Requirements

### To Compile

These applications can be compiled on any architecture natively in a Linux environment.

To compile, some software packages are required. These can be installed by running:

- sudp apt install cmake
- sudp apt install g++

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

Copyright 2024, Network Optix, All rights reserved.

## Directory structure

```
.
├── CMakeLists.txt
├── README.md
├── socket-json-postprocessor-c-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── deps
│   │   ├── yyjson.c
│   │   └── yyjson.h
│   └── src
│       └── main.c
├── socket-json-postprocessor-c-image-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── deps
│   │   ├── yyjson.c
│   │   └── yyjson.h
│   └── src
│       └── main.c
├── socket-json-postprocessor-python-example
│   ├── CMakeLists.txt
│   ├── README.md
│   ├── postprocessor-python-example.py
│   └── requirements.txt
└── socket-json-postprocessor-python-image-example
    ├── CMakeLists.txt
    ├── README.md
    ├── postprocessor-python-image-example.py
    └── requirements.txt
```