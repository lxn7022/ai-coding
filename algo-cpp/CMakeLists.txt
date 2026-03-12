cmake_minimum_required(VERSION 3.14)
project(algo-cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

if(MSVC)
  add_compile_options(/utf-8)
endif()

# 算法库
add_library(algo_list algo_list.cpp)
target_include_directories(algo_list PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

add_library(algo_tree algo_tree.cpp)
target_include_directories(algo_tree PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# 独立可执行：运行 print_tree 演示
add_executable(test_algo test_algo.cpp)
target_link_libraries(test_algo PRIVATE algo_tree)
target_include_directories(test_algo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# 单元测试（Google Test）
option(ALGO_CPP_BUILD_TESTS "Build unit tests (Google Test)" ON)
if(ALGO_CPP_BUILD_TESTS)
  include(FetchContent)
  FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        v1.14.0
  )
  set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
  FetchContent_MakeAvailable(googletest)

  enable_testing()
  add_executable(algo_list_tests test_algo_list.cpp)
  target_link_libraries(algo_list_tests PRIVATE algo_list GTest::gtest GTest::gtest_main)
  target_include_directories(algo_list_tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME algo_list_tests COMMAND algo_list_tests)

  add_executable(algo_tree_tests test_algo_tree.cpp)
  target_link_libraries(algo_tree_tests PRIVATE algo_tree GTest::gtest GTest::gtest_main)
  target_include_directories(algo_tree_tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME algo_tree_tests COMMAND algo_tree_tests)
endif()
