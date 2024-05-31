# excluded main.c from sources
set(SOURCES_MINUS_MAIN ${SOURCES})
list(REMOVE_ITEM SOURCES_MINUS_MAIN ${SOURCE_DIR}/main.c)

# enumerate subdirectories
add_subdirectory(sample)
