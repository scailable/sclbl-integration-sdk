# Add target to build everything at once
add_custom_target(preprocessor-python-tensor-example ALL
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMAND pip install -r ../nxai-utilities/python-utilities/requirements.txt
    COMMAND pip install -r requirements.txt
    COMMAND pyinstaller preprocessor-python-tensor-example.py --onefile --workpath ${CMAKE_CURRENT_BINARY_DIR}/build --distpath ${CMAKE_CURRENT_BINARY_DIR} --paths=${CMAKE_SOURCE_DIR}/nxai-utilities/python-utilities -y
)