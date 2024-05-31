# definition build target name
set(TARGET_NAME SampleProject)

add_executable(${TARGET_NAME} ${SOURCE_DIR}/main.c) 
# add_library(${TARGET_NAME} STATIC ${SOURCES})
# set features
target_compile_features(${TARGET_NAME} PUBLIC c_std_17)
# set options
target_compile_options(${TARGET_NAME} PRIVATE
	${WARNING_OPT}
	$<$<CONFIG:Debug>:${DEBUG_OPT}>
	$<$<CONFIG:Release>:${NODEBUG_OPT}>
)

# add source files
target_sources(${TARGET_NAME} PRIVATE ${SOURCES})
# add header directories 
target_include_directories(${TARGET_NAME} PRIVATE
	${SOURCE_DIR}/
)
# link libraries
target_link_libraries(${TARGET_NAME} PRIVATE
	${LIBS}
	$<$<CONFIG:Debug>:${DEBUG_LIBS}>
)

# definition preprocessor
# target_compile_definitions(${TARGET_NAME} PRIVATE 
# 	_GLIBCXX_USE_CXX11_ABI=1
# )
