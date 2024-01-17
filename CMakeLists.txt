cmake_minimum_required(VERSION 3.10.2)

project(sclbl-integration-examples)

# Add Scailable C Utilities for all subprojects
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/sclbl-utilities)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/sclbl-utilities/include)

# Add Socket Json Postprocessor project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/socket-json-postprocessor-c-example)

# Add Socket MsgPack Postprocessor project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/socket-msgpack-postprocessor-c-example)

# Add Socket C Image Postprocessor project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/socket-json-postprocessor-c-image-example)

# Add Socket Json Postprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/socket-json-postprocessor-python-example)

# Add Socket Json Image Postprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/socket-json-postprocessor-python-image-example)

# Add Socket MsgPack Image Postprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/socket-msgpack-postprocessor-python-example)

# # Add installation option
install(TARGETS
    postprocessor-example
    postprocessor-tensor-example
    postprocessor-msgpack-example
    DESTINATION /opt/sclbl/postprocessors/
)
install(PROGRAMS
    ${CMAKE_CURRENT_BINARY_DIR}/socket-json-postprocessor-python-example/postprocessor-python-example
    ${CMAKE_CURRENT_BINARY_DIR}/socket-json-postprocessor-python-image-example/postprocessor-python-image-example
    ${CMAKE_CURRENT_BINARY_DIR}/socket-msgpack-postprocessor-python-example/postprocessor-msgpack-python-example
    DESTINATION /opt/sclbl/postprocessors/
)