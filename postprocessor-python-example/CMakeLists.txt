# Add target to build everything at once
add_custom_target(postprocessor-python-example ALL
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMAND pip install -r ../sclbl-utilities/python-utilities/requirements.txt
    COMMAND pip install -r requirements.txt
    COMMAND pyinstaller postprocessor-python-example.py --onefile --workpath ${CMAKE_CURRENT_BINARY_DIR}/build --distpath ${CMAKE_CURRENT_BINARY_DIR} --paths=${CMAKE_SOURCE_DIR}/sclbl-utilities/python-utilities -y
)