cmake_minimum_required(VERSION 3.2)

project(SclblCUtilities)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

add_library(sclbl-c-utilities
    ${CMAKE_CURRENT_SOURCE_DIR}/src/sclbl_socket_utils.c
)