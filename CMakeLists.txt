cmake_minimum_required(VERSION 3.5.1)

# set the project name
project(Simple_testbed VERSION 1.0)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)


SET(CMAKE_BUILD_TYPE "Debug")
SET(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -O0 -Wall -g2 -ggdb")
SET(CMAKE_CXX_FLAGS_RELEASE "$ENV{CXXFLAGS} -O3 -Wall")

# add the executable
add_executable(avail-client client.cpp utils.h utils.cpp)
add_executable(avail-server server.cpp)
add_executable(fake-client fakeclient.cpp utils.h utils.cpp)
add_executable(hw-server hardware.c)
add_executable(hw-client hardware.c)