# Google Test: FetchContent 拉取，无需预先安装
include(FetchContent)
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG        v1.14.0
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

# 单元测试可执行
add_executable(rbac_tests
  rbac_engine_test.cpp
  persistence_test.cpp
)
target_link_libraries(rbac_tests PRIVATE rbac GTest::gtest GTest::gtest_main)
target_include_directories(rbac_tests PRIVATE ${CMAKE_SOURCE_DIR}/include)

add_test(NAME rbac_tests COMMAND rbac_tests)
