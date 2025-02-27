# Add target to build everything at once
set(PROCESSOR_NAME "postprocessor-python-noresponse-example")
add_custom_target(${PROCESSOR_NAME} ALL
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMAND pip install -r ../nxai-utilities/python-utilities/requirements.txt
    COMMAND pip install -r requirements.txt
    COMMAND cp ${CMAKE_CURRENT_SOURCE_DIR}/../nxai-utilities/python-utilities/communication_utils.py ${CMAKE_CURRENT_SOURCE_DIR}
    COMMAND nuitka ${CMAKE_CURRENT_SOURCE_DIR}/${PROCESSOR_NAME}.py --onefile --output-filename=${PROCESSOR_NAME} --output-dir=${CMAKE_CURRENT_BINARY_DIR}
    COMMAND rm ${CMAKE_CURRENT_SOURCE_DIR}/communication_utils.py
)