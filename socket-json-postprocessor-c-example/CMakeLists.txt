
cmake_minimum_required(VERSION 3.10.2)

project(sclbl-socket-c-postprocessor-example)

# Generate compile commands
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)


add_executable(postprocessor-example
        src/main.c
        # Add local dependencies
        deps/yyjson.c
)

target_include_directories(postprocessor-example PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_include_directories(postprocessor-example PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/deps)

# Add compile options for all targets
target_compile_options(postprocessor-example PUBLIC 
-funsafe-math-optimizations -s -fno-delete-null-pointer-checks -fno-math-errno -Wno-unknown-pragmas -ffunction-sections
        -fPIC -Wall -Wextra -Wshadow -Wmissing-declarations -fno-math-errno
-fdata-sections -ffunction-sections
)

if (CMAKE_BUILD_TYPE STREQUAL "Release")
  target_compile_options(postprocessor-example PUBLIC
    -O3 -Ofast
  )
endif()

# Add linker options
target_link_options(postprocessor-example PUBLIC -Wl,--gc-sections -Wl,--as-needed -static -pthread )

# Link generic libraries
target_link_libraries(postprocessor-example m dl rt)

# Link utilities libraries
target_link_libraries(postprocessor-example sclbl-c-utilities)
