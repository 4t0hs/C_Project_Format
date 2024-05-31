enable_testing()
set(TEST_TARGET_NAME SampleProjectTester)

file(GLOB_RECURSE TEST_SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/*.c)

add_executable(${TEST_TARGET_NAME} ${CMAKE_CURRENT_SOURCE_DIR}/main.c)
target_compile_features(${TEST_TARGET_NAME} PUBLIC c_std_17)

target_sources(${TEST_TARGET_NAME} PRIVATE
	${TEST_SOURCES}
)

target_include_directories(${TEST_TARGET_NAME} PRIVATE
	${CSV_INLCUDE}
	${PROJECT_HOME}/include
	${CMAKE_CURRENT_SOURCE_DIR}
)

# target_link_directories(${TEST_TARGET_NAME} PRIVATE
# )

target_link_libraries(${TEST_TARGET_NAME}
	${LIBS}
	${DEBUG_LIBS}
)

target_compile_options(${TEST_TARGET_NAME} PRIVATE
	${WARNING_OPT}
	$<$<CONFIG:Debug>:${DEBUG_OPT}>
	$<$<CONFIG:Release>:${NODEBUG_OPT}>
)
