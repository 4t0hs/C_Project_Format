cmake_minimum_required(VERSION 3.2)
project(LibCsv C)

#
# definition common variables
#
set(PROJECT_HOME ${PROJECT_SOURCE_DIR})
set(SOURCE_DIR ${PROJECT_HOME}/src)

# compile options
set(NODEBUG_OPT
-O2
)
Set(DEBUG_OPT 
-g3
-ggdb
-O0
)
set(WARNING_OPT
-Wall
-Wextra
)
# libraries
set(LIBS
)
set(DEBUG_LIBS
)
# C files
file(GLOB_RECURSE SOURCES ${SOURCE_DIR}/*.c)

message(STATUS "Project home: " ${PROJECT_HOME})
message(STATUS "Source directory: " ${SOURCE_DIR})
message(STATUS "C source files: " ${SOURCES})

#
# sub directories
#
add_subdirectory(src)
add_subdirectory(tests)
