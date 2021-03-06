add_executable (find_min_cost find_min_cost.cpp)
set_target_properties(find_min_cost PROPERTIES
                                    INCLUDE_DIRECTORIES ${Boost_INCLUDE_DIRS})
target_link_libraries(find_min_cost PRIVATE ${Boost_LIBRARIES})
target_link_libraries(find_min_cost PRIVATE ${GLOG_LIBRARY})
target_link_libraries(find_min_cost PUBLIC ${PROJECT_NAME_STR})

add_executable (incremental_min_cost incremental_min_cost.cpp)
set_target_properties(incremental_min_cost PROPERTIES
                                    INCLUDE_DIRECTORIES ${Boost_INCLUDE_DIRS})
target_link_libraries(incremental_min_cost PRIVATE ${Boost_LIBRARIES})
target_link_libraries(incremental_min_cost PRIVATE ${GLOG_LIBRARY})
target_link_libraries(incremental_min_cost PUBLIC ${PROJECT_NAME_STR})

add_executable (incremental_snapshots incremental_snapshots.cpp)
set_target_properties(incremental_snapshots PROPERTIES
                                    INCLUDE_DIRECTORIES ${Boost_INCLUDE_DIRS})
target_link_libraries(incremental_snapshots PRIVATE ${Boost_LIBRARIES})
target_link_libraries(incremental_snapshots PRIVATE ${GLOG_LIBRARY})
target_link_libraries(incremental_snapshots PUBLIC ${PROJECT_NAME_STR})

add_executable (incremental_snapshots_compare incremental_snapshots_compare.cpp)
set_target_properties(incremental_snapshots_compare PROPERTIES
                                    INCLUDE_DIRECTORIES ${Boost_INCLUDE_DIRS})
target_link_libraries(incremental_snapshots_compare PRIVATE ${Boost_LIBRARIES})
target_link_libraries(incremental_snapshots_compare PRIVATE ${GLOG_LIBRARY})
target_link_libraries(incremental_snapshots_compare PUBLIC ${PROJECT_NAME_STR})

add_executable (incremental_statistics incremental_statistics.cpp)
set_target_properties(incremental_statistics PROPERTIES
                                    INCLUDE_DIRECTORIES ${Boost_INCLUDE_DIRS})
target_link_libraries(incremental_statistics PRIVATE ${Boost_LIBRARIES})
target_link_libraries(incremental_statistics PRIVATE ${GLOG_LIBRARY})
target_link_libraries(incremental_statistics PUBLIC ${PROJECT_NAME_STR})

add_executable (partial_incremental_min_cost partial_incremental_min_cost.cpp)
set_target_properties(partial_incremental_min_cost PROPERTIES
                                    INCLUDE_DIRECTORIES ${Boost_INCLUDE_DIRS})
target_link_libraries(partial_incremental_min_cost PRIVATE ${Boost_LIBRARIES})
target_link_libraries(partial_incremental_min_cost PRIVATE ${GLOG_LIBRARY})
target_link_libraries(partial_incremental_min_cost PUBLIC ${PROJECT_NAME_STR})

add_executable (snapshot_solver snapshot_solver.cpp)
target_link_libraries(snapshot_solver PRIVATE ${GLOG_LIBRARY})

add_executable (dimacs_echo dimacs_echo.cpp)
target_link_libraries (dimacs_echo LINK_PUBLIC ${PROJECT_NAME_STR})

if (LEMON_FOUND)
    add_executable(lemon_min_cost lemon_min_cost.cpp)
    set_target_properties(lemon_min_cost PROPERTIES
                                         INCLUDE_DIRECTORIES ${LEMON_INCLUDE_DIRS})
    target_link_libraries(lemon_min_cost PRIVATE ${LEMON_LIBRARIES})
endif()
