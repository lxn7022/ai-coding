cmake_minimum_required(VERSION 3.14)
project(rbac-cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

# MSVC：源文件与执行字符集使用 UTF-8，避免中文乱码
if(MSVC)
  add_compile_options(/utf-8)
endif()

# 库：RBAC 核心 + 持久化
add_library(rbac
  src/rbac_engine.cpp
  src/persistence.cpp
)
target_include_directories(rbac PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

# 可执行示例
add_executable(rbac_demo src/main.cpp)
target_link_libraries(rbac_demo PRIVATE rbac)

# 单元测试（tests/ 使用 FetchContent 拉取 GTest，首次可能较慢或卡住）
option(RBAC_BUILD_TESTS "Build unit tests (requires downloading Google Test)" ON)
if(RBAC_BUILD_TESTS)
  add_subdirectory(tests)
endif()

# 可选：安装
install(TARGETS rbac rbac_demo
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
)
install(DIRECTORY include/rbac DESTINATION include)
