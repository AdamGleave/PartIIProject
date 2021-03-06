add_definitions(-DCMAKE_SRC_DIR="${PROJECT_SOURCE_DIR}")

add_executable(test_task_assignment test_task_assignment.cpp)
target_link_libraries(test_task_assignment PRIVATE gtest gtest_main ${PROJECT_NAME_STR})

add_executable(test_networks test_networks.cpp)
target_link_libraries(test_networks PRIVATE gtest gtest_main ${PROJECT_NAME_STR})

add_executable(test_dynamic_maintain_optimality test_dynamic_maintain_optimality.cpp)
target_link_libraries(test_dynamic_maintain_optimality PRIVATE gtest gtest_main ${PROJECT_NAME_STR})

add_test(task_assignment test_task_assignment)
add_test(networks test_networks)
add_test(dynamic_maintain_optimality test_dynamic_maintain_optimality)
add_test(NAME flowsolver_full_tests 
         COMMAND ./test_algorithms.py
         WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
add_test(NAME flowsolver_incremental_graph_tests 
         COMMAND ./test_incremental_graph.py
         WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
add_test(NAME flowsolver_incremental_solver_tests 
         COMMAND ./test_incremental_solver.py
         WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})