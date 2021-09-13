cmake_minimum_required(VERSION 3.12)

project(RANSAC_comp)

add_subdirectory(efficient_ransac)

include_directories(${CMAKE_CURRENT_LIST_DIR}/efficient_ransac)

add_executable(${CMAKE_PROJECT_NAME} main.cpp)

target_link_libraries(${CMAKE_PROJECT_NAME} efficient_ransac)
