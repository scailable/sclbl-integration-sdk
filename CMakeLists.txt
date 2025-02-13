cmake_minimum_required(VERSION 3.10.2)

project(nxai-integration-examples)

# Add Scailable C Utilities for all subprojects
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/nxai-utilities)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/nxai-utilities/include)

# Add C Postprocessor project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-c-example)

# Add C Image Postprocessor project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-c-image-example)

# Add C Raw Postprocessor project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-c-raw-example)

# Add Postprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-python-example)

# Add Image Postprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-python-image-example)

# Add Confidence Postprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-python-confidences-example)

# Add Settings Postprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-python-settings-example)

# Add Postprocessor Python Events project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-python-events-example)

# Add Postprocessor Python NoResponse project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-python-noresponse-example)

# Add Cloud Inference Postprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/postprocessor-cloud-inference-example)

# Add Image Preprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/preprocessor-python-image-example)

# Add Tensor Preprocessor Python project
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/preprocessor-python-tensor-example)

# # Add installation option
install(TARGETS
    postprocessor-c-example
    postprocessor-c-image-example
    postprocessor-c-raw-example
    DESTINATION /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/
)

# Install postprocessors
install(PROGRAMS
    ${CMAKE_CURRENT_BINARY_DIR}/postprocessor-python-example/postprocessor-python-example
    ${CMAKE_CURRENT_BINARY_DIR}/postprocessor-python-image-example/postprocessor-python-image-example
    ${CMAKE_CURRENT_BINARY_DIR}/postprocessor-python-confidences-example/postprocessor-python-confidences-example
    ${CMAKE_CURRENT_BINARY_DIR}/postprocessor-python-settings-example/postprocessor-python-settings-example
    ${CMAKE_CURRENT_BINARY_DIR}/preprocessor-image-python-example/preprocessor-image-python-example
    ${CMAKE_CURRENT_BINARY_DIR}/preprocessor-tensor-python-example/preprocessor-tensor-python-example
    ${CMAKE_CURRENT_BINARY_DIR}/postprocessor-python-noresponse-example/postprocessor-python-noresponse-example
    ${CMAKE_CURRENT_BINARY_DIR}/postprocessor-python-events-example/postprocessor-python-events-example
    ${CMAKE_CURRENT_BINARY_DIR}/postprocessor-cloud-inference-example/postprocessor-cloud-inference-example
    DESTINATION /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/postprocessors/
)

# Install preprocessors
install(PROGRAMS
    ${CMAKE_CURRENT_BINARY_DIR}/preprocessor-python-example/preprocessor-python-image-example
    ${CMAKE_CURRENT_BINARY_DIR}/preprocessor-python-example/preprocessor-python-tensor-example
    DESTINATION /opt/networkoptix-metavms/mediaserver/bin/plugins/nxai_plugin/nxai_manager/preprocessors/
)