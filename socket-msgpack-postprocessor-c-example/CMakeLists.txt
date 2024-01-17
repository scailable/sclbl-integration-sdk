
cmake_minimum_required(VERSION 3.10.2)

project(sclbl-socket-c-postprocessor-msgpack-example)

# Generate compile commands
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_executable(postprocessor-msgpack-example
  src/main.c

  # Add local dependencies
  deps/mpack.c
)

target_include_directories(postprocessor-msgpack-example PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_include_directories(postprocessor-msgpack-example PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/deps)

# Add compile options for all targets
target_compile_options(postprocessor-msgpack-example PUBLIC
  -funsafe-math-optimizations -s -fno-delete-null-pointer-checks -fno-math-errno -Wno-unknown-pragmas -ffunction-sections
  -fPIC -Wall -Wextra -Wshadow -Wmissing-declarations -fno-math-errno
  -fdata-sections -ffunction-sections
)

if(CMAKE_BUILD_TYPE STREQUAL "Release")
  target_compile_options(postprocessor-msgpack-example PUBLIC
    -O3 -Ofast
  )
endif()

# Add linker options
target_link_options(postprocessor-msgpack-example PUBLIC -Wl,--gc-sections -Wl,--as-needed -static -pthread)

# Link generic libraries
target_link_libraries(postprocessor-msgpack-example m dl rt)

# Link utilities libraries
target_link_libraries(postprocessor-msgpack-example sclbl-c-utilities)
