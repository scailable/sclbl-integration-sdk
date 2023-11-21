cmake_minimum_required(VERSION 3.10.2)

project(sclbl-integration-examples)

# Add Scailable C Utilities for all subprojects
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/sclbl-utilities)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/sclbl-utilities/include)

# Add Socket Json Postprocessor project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/socket-json-postprocessor-c-example)

# Add Socket Json Postprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/socket-json-postprocessor-python-example)

## Add installation option
install(TARGETS 
            postprocessor-example
        DESTINATION /opt/sclbl/postprocessors/
)
install(PROGRAMS
            ${CMAKE_CURRENT_BINARY_DIR}/socket-json-postprocessor-python-example/postprocessor-python-example
        DESTINATION /opt/sclbl/postprocessors/
        )