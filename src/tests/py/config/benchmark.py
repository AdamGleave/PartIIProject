#!/usr/bin/env python3

# Example config file
# Mock-up only

import os, sh

MAKE_FLAGS = []

try:
  # allow settings to be overridden on a local basis
  from config.benchmark_local import *
except ImportError:
  pass

from config.common import *

WORKING_DIRECTORY = "/tmp/flowsolver_benchmark"
RESULT_ROOT = os.path.join(PROJECT_ROOT, "benchmark")
FIRMAMENT_ROOT = os.path.join(os.path.dirname(PROJECT_ROOT), "firmament")

##### Executables
 
GOOGLE_TRACE_SIMULATOR_PATH = os.path.join(FIRMAMENT_ROOT, 
                      "build", "sim", "trace-extract", "google_trace_simulator")
GOOGLE_TRACE_SIMULATOR_ARGS = ["--logtostderr"]
GOOGLE_TRACE_SIMULATOR = sh.Command(GOOGLE_TRACE_SIMULATOR_PATH) \
                           .bake(*GOOGLE_TRACE_SIMULATOR_ARGS)

##### Dataset
# Note these variables are not used by the suite at all. They are provided
# for convenience within the config, to allow us to reference particular sets
# of files by a short name.

### Full graphs
FULL_DATASET = {
  ### Networks representing clusters
  
  # these are too small to be useful for a benchmark: but handy to quickly test
  # the benchmark script itself
  "development_only": ["clusters/synthetic/firmament/graph_4m_2crs_10j.in", 
                       "clusters/synthetic/handmade/small_graph.in"],
  # 100 machine networks
  "synthetic_small": graphGlob("clusters/synthetic/firmament/graph_100m_*"),
  # 1000 machine networks
  "synthetic_large": ["clusters/synthetic/firmament/graph_1000m_32j_100t_10p.in"],
  # Network from Google cluster trace
  "google": ["clusters/natural/google_trace/google_all.in"],
  
  # Graphs after 1 hour into Google Trace. Using Octopus cost model.
  # Generated with CS2 solver, 10 us scheduling interval.
  # Have graphs with 100, 1000 & 10,000 machines.
  "octopus_1hour": graphGlob("clusters/natural/google_trace/octopus/1hour/*"),
  
  ### General flow networks
  ### See https://lemon.cs.elte.hu/trac/lemon/wiki/MinCostFlowData
  
  ## ROAD
  # ROAD-PATHS: all arc capacities one
  # ROAD-FLOW: capacity set to 40/60/80/100 depending on road category
  "road_paths": graphGlob("general/natural/road/road_paths_*.min"),
  "road_flow": graphGlob("general/natural/road/road_flow_*.min"),
  "road": graphGlob("general/natural/road/road_*.min"),
  
  ## VISION
  # VISION-RND: The arc costs are selected uniformly at random.
  # VISION-PROP: The cost of an arc is approximately proportional to its capacity.
  # VISION-INV: The cost of an arc is approximately inversely proportional to its capacity.
  "vision_rnd": graphGlob("general/natural/vision/vision_rnd_*.min"),
  "vision_prop": graphGlob("general/natural/vision/vision_prop_*.min"),
  "vision_inv": graphGlob("general/natural/vision/vision_inv_*.min"),
  "vision": graphGlob("general/natural/vision/vision_*.min"),
  
  ## NETGEN
  # NETGEN-8: Sparse networks, with m = 8n. Capacities and costs uniform random.
  #           Supply and demand nodes are sqrt(n);
  #           average supply per suppply node is 1000.
  # NETGEN-SR: As above, but m = n*sqrt(n) (relatively dense)
  # NETGEN-LO-8: As NETGEN-8, but with much lower average supply, around 10.
  # NETGEN-LO-SR: As NETGEN-SR, but with much lower average supply, around 10.
  # NETGEN-DEG: n=4096 fixed, average outdegree ranges from 2 to n/2. 
  #             Otherwise, as for NETGEN-8. 
  "netgen_8": graphGlob("general/synthetic/netgen/netgen_8_*.min"), 
  "netgen_sr": graphGlob("general/synthetic/netgen/netgen_sr_*.min"),
  "netgen_lo_8": graphGlob("general/synthetic/netgen/netgen_lo_8_*.min"),
  "netgen_lo_sr": graphGlob("general/synthetic/netgen/netgen_lo_sr_*.min"),
  "netgen_deg": graphGlob("general/synthetic/netgen/netgen_deg_*.min"),
  
  ## GOTO (Grid On Torus)
  # GOTO-8: Equivalent parameters to NETGEN-8.
  # GOTO-SR: Equivalent parameters to NETGEN-SR.
  "goto_8": graphGlob("general/synthetic/goto/goto_8_*.min"),
  "goto_sr": graphGlob("general/synthetic/goto/goto_sr_*.min"),
}

FULL_DATASET["synthetic"] = FULL_DATASET["synthetic_small"] \
                          + FULL_DATASET["synthetic_large"]

all_files = set()
for files in FULL_DATASET.values():
  all_files.update(files)
FULL_DATASET["all"] = all_files

### Incremental graphs
INCREMENTAL_DATASET = {
  # Not real data, and too small to be useful. Good for testing benchmark script.
  "development_only": ["clusters/natural/google_trace/tiny_trace.imin"],
  # CS2 on the small Google trace. Only the first 7 deltas.
  "google_small_trace_truncated": ["clusters/natural/google_trace/small_trace.imin"],
}

### Google cluster trace(s)
TRACE_DATASET = {
  "tiny_trace": 
  {
    "dir": os.path.join(TRACE_ROOT, "tiny_trace"),
    "num_files": 1,
  },
  "small_trace": {
    "dir": os.path.join(TRACE_ROOT, "small_trace"),
    "num_files": 1,
  },
  "google_trace": {
    "dir": os.path.join(TRACE_ROOT, "google_trace"),
    "num_files": 500,
  },
}

SECOND = 10**6 # 1 second in microseconds
TRACE_START = 600*SECOND
# timestamp of last event in trace
TRACE_LENGTH = 2506199602822
RUNTIME_MAX = 2**64 - 1

def percentRuntime(p):
  return TRACE_START + (TRACE_LENGTH - TRACE_START) * (p / 100.0)

def absoluteRuntime(s):
  return TRACE_START + (s * 1000 * 1000)

##### Compilers

STANDARD_FLAGS = "-DNDEBUG" 

# Template
# "cc": C compiler
# "cxx": C++ compiler
# "flags": C & C++ flags
# "cflags": C-only flags
# "cxxflags": C++-only flags

COMPILER_GCC = {
    "cc": "gcc",
    "cxx": "g++",
}

COMPILER_CLANG = {
    "cc": "clang",
    "cxx": "clang++",
} 

COMPILERS = {
  "gcc_debug": extendDict(COMPILER_GCC, {"flags": "-g"}),
  "gcc_O0": extendDict(COMPILER_GCC, {"flags": "-O0"}),
  "gcc_O1": extendDict(COMPILER_GCC, {"flags": "-O1 -DNDEBUG"}),
  "gcc_O2": extendDict(COMPILER_GCC, {"flags": "-O2 -DNDEBUG"}),
  "gcc_O3": extendDict(COMPILER_GCC, {"flags": "-O3 -DNDEBUG"}),
  "clang_debug": extendDict(COMPILER_CLANG, {"flags": "-g"}),
  "clang_O0": extendDict(COMPILER_CLANG, {"flags": "-O0"}),
  "clang_O1": extendDict(COMPILER_CLANG, {"flags": "-O1 -DNDEBUG"}),
  "clang_O2": extendDict(COMPILER_CLANG, {"flags": "-O2 -DNDEBUG"}),
  "clang_O3": extendDict(COMPILER_CLANG, {"flags": "-O3 -DNDEBUG"}),
}

DEFAULT_COMPILER = "gcc_O3"

def compilerTests(test_cases, compilers):
  d = {}
  for test_name, test_config in test_cases.items():
    for compiler in compilers:
      key = test_name + "_" + compiler
      value = test_config.copy()
      value["compiler"] = compiler
      d.update({key : value})
  return d

##### Implementations

### Full solvers
FULL_IMPLEMENTATIONS = {
  ### My implementations - latest
  "ap_latest": {
    "version": "master",
    "target": "find_min_cost",
    "path": "bin/find_min_cost",
    "arguments" : ["augmenting_path", "--quiet"],
    "offline_arguments": ["--flow", "false"]
  },
  "cc_latest": {
    "version": "master",
    "target": "find_min_cost",
    "path": "bin/find_min_cost",
    "arguments" : ["cycle_cancelling", "--quiet"], 
    "offline_arguments": ["--flow", "false"]
  },
  "cs_latest": {
    "version": "master",
    "target": "find_min_cost",
    "path": "bin/find_min_cost",
    "arguments": ["cost_scaling", "--quiet"],
    "offline_arguments": ["--flow", "false"]
  },
  "relax_latest": {
    "version": "master",
    "target": "find_min_cost",
    "path": "bin/find_min_cost",
    "arguments": ["relax", "--quiet"],
    "offline_arguments": ["--flow", "false"]
  },

  ### Reference implementations
  ### (Not all of them -- LEMON included below)
  "cs_goldberg": {
    "version": "master",
    "target": "cs2.exe",
    "path": "cs2/cs2",
    "offline_arguments" : ["-f", "false"]
  },
  "relax_frangioni": {
    "version": "master",
    "target": "RelaxIV_original",
    "path": "RelaxIV/RelaxIV_original",
    "offline_arguments": ["--flow", "false"]
  },
                        
  ### My implementations - specific versions
  ### These are used for testing particular optimisations which have been applied
  
  ## Augmenting path    
  "ap_bigheap": {
     "version": "1540fc0",
     "target": "find_min_cost",
     "path": "bin/find_min_cost",
     "arguments" : ["augmenting_path"]
  },
   "ap_smallheap_vector": {
     "version": "41c6852",
     "target": "find_min_cost",
     "path": "bin/find_min_cost",
     "arguments" : ["augmenting_path"]
  },
   "ap_smallheap_map": {
     "version": "cd42c6e",
     "target": "find_min_cost",
     "path": "bin/find_min_cost",
     "arguments" : ["augmenting_path"]
  },
  "ap_full_djikstra": {
     "version": "opt_ap_fulldjikstra",
     "target": "find_min_cost",
     "path": "bin/find_min_cost",
     "arguments" : ["augmenting_path"]
  },
  ## RELAX
  "relax_firstworking": {
    "version": "73e0b68",
    "target": "find_min_cost",
    "path": "bin/find_min_cost",
    "arguments": ["relax"]
  },
  "relax_cache_zerorc": {
    "version": "afe3a21",
    "target": "find_min_cost",
    "path": "bin/find_min_cost",
    "arguments": ["relax"]
  },
  "relax_cache_all": {
    "version": "86f751f",
    "target": "find_min_cost",
    "path": "bin/find_min_cost",
    "arguments": ["relax"]
  },
  ## Cost scaling
  "cs_wave": {
   "version": "cs_wave",
   "target": "find_min_cost",
   "path": "bin/find_min_cost",
   "arguments" : ["cost_scaling"]
  },
  "cs_vertexqueue": {
   "version": "1653e9e",
   "target": "find_min_cost",
   "path": "bin/find_min_cost",
   "arguments" : ["cost_scaling"]
  },
  ## Parser
  # Note some of these implementations are so old they don't report ALGOTIME.
  # (But you don't want that measure anyway, since you want to capture
  # the parser *overhead*!)
  "parser_unoptimised": {
    "version": "opt_parser_unoptimised",
    "target": "find_min_cost",
    "path": "bin/find_min_cost",
    "arguments" : ["cost_scaling"]
  },
  "parser_ignore_zero_capacity": {
    "version": "opt_parser_ignore_zero_cap",
    "target": "find_min_cost",
    "path": "bin/find_min_cost",
    "arguments" : ["cost_scaling"]
  },
   "parser_set_of_arcs": {
     "version": "opt_parser_set_arc",
     "target": "find_min_cost",
     "path": "bin/find_min_cost",
     "arguments" : ["cost_scaling"]
  },
}

# Reference implementations - LEMON
LEMON_ALGOS = ["scc", "mmcc", "cat", "ssp", "cas", "cos", "ns"]
for algo in LEMON_ALGOS:
  FULL_IMPLEMENTATIONS["lemon_" + algo] = {
    "version": "master",
    "target": "lemon_min_cost",
    "path": "bin/lemon_min_cost",
    "arguments": ["-" + algo]
  }

### Incremental solvers
MY_INCREMENTAL_OFFLINE_ARGS = ["--flow", "false"]
INCREMENTAL_IMPLEMENTATIONS = {
  ### My solvers - latest
  "ap_latest": {
    "version": "master",
    "target": "incremental_min_cost",
    "path": "bin/incremental_min_cost",
    "arguments": ["augmenting_path", "--quiet"],
    "offline_arguments": MY_INCREMENTAL_OFFLINE_ARGS,
   },
   "relax_latest": {
    "version": "master",
    "target": "incremental_min_cost",
    "path": "bin/incremental_min_cost",
    "arguments": ["relax", "--quiet"],
    "offline_arguments": MY_INCREMENTAL_OFFLINE_ARGS,
   },
  ### RELAX Frangioni with incremental additions
  # Latest
  "relaxf_latest": {
    "version": "master",
    "target": "RelaxIV_incremental",
    "path": "RelaxIV/RelaxIV_incremental",
    "arguments": ["--quiet"],
    "offline_arguments": MY_INCREMENTAL_OFFLINE_ARGS,
  },
  # First version that fully works. Includes bugfix to solve uninitialized value
  # access in tfstin/tnxtin/etc. 
  "relaxf_firstworking": {
    "version": "b5721bb",
    "target": "incremental",
    "path": "RelaxIV/RelaxIV_incremental",
  },
}

IMPLEMENTATIONS = mergeDicts([FULL_IMPLEMENTATIONS, INCREMENTAL_IMPLEMENTATIONS],
                             ["f", "i"], ["full", "incremental"])

##### Test cases

DEFAULT_TIMEOUT = 300 # s, i.e. 5 minutes

### Tests on full graphs, comparing only full solvers
FULL_TESTS = {
  # For testing benchmark suite only
  "development_only": {
    "files": FULL_DATASET["development_only"],
    "iterations": 3,
    "tests": {
      "my": {
        "implementation": "f_cc_latest",
      },
      "goldberg": {
        "implementation": "f_cs_goldberg",
      },
    },
  },   
  "development_only_compilers": {
    "files": FULL_DATASET["google"],
    "iterations": 1,
    "tests": {
      "goldberg_slow": {
        "implementation": "f_cs_goldberg",
        "compiler": "gcc_debug"
      },
      "goldberg_fast": {
        "implementation": "f_cs_goldberg",
        "compiler": "gcc_O3"
      },
    },
  },
              
  ### Optimisation tests
  ## Augmenting path
               
  # Big heap: keeps all vertices in the priority queue. O(n) to create, but
  # all operations are O(n lg n) afterwards.
  # Small heap: keeps only vertices with finite distance in priority queue.
  # O(1) to create, but has to pay insertion cost. Operations cheaper provided
  # there are vertices not in queue.
  # Performance will ultimately depend on how many vertices get explored before
  # Djikstra quits.
  # Additionally, have the choice between maintaining the reverse index
  # as a vector or a map. Vector will give guaranteed O(1) lookup, and we 
  # don't care about the memory consumption, but map may actually perform 
  # better since it can be better cached.
  "opt_ap_big_vs_small_heap": {
    "files": FULL_DATASET["octopus_1hour"],
    "iterations": 5,
    "tests": {
      "big": {
        "implementation": "f_ap_bigheap",
      },
      "small_vector": {
        "implementation": "f_ap_smallheap_vector",
      },
      "small_map": {
        "implementation": "f_ap_smallheap_map",
      },
    },
  },
              
  # Test early termination of Djikstra's algorithm
  "opt_ap_full_vs_partial_djikstra": {
    "files": FULL_DATASET["octopus_1hour"],
    "iterations": 5,
    "tests": {
      "full": {
        "implementation": "f_ap_full_djikstra",
      },
      "partial": {
        "implementation": "f_ap_latest",
      },
    }, 
  },
              
  ## Relaxation
  
  # Caching arcs crossing the cut
  # zerorc case: only zero reduced cost cuts
  # all case: every arc crossing the cut (separated into positive and zero rc)
  "opt_relax_cache_arcs": {
    "files": FULL_DATASET["octopus_1hour"],
    "iterations": 5,
    "tests": {
      "none": {
        "implementation": "f_relax_firstworking",
      },
      "cache_zerorc": {
        "implementation": "f_relax_cache_zerorc",
      },
      "cache_all": {
        "implementation": "f_relax_cache_all",
      },
    }, 
  },
              
  ## Cost scaling
  "opt_cs_wave_vs_fifo": {
    "files": FULL_DATASET["octopus_1hour"],
    "iterations": 5,
    "tests": {
      "wave": {
        "implementation": "f_cs_wave",
      },
      "fifo": {
        "implementation": "f_cs_vertexqueue",
      },
    },
  },
  "opt_cs_scaling_factor": {
    "files": FULL_DATASET["octopus_1hour"],
    "iterations": 5,
    "tests": { 
      str(x): {
        "implementation": "f_cs_latest",
        "arguments": ["--scaling-factor", x]
      } for x in range(2,32)
    }
  },
              
 ## DIMACS parser
 "opt_parser_set_vs_getarc": {
    "files": FULL_DATASET["octopus_1hour"],
    "iterations": 5,
    "tests": {
      "set": {
        "implementation": "f_parser_set_of_arcs",
      },
      "getarc": {
        "implementation": "f_parser_ignore_zero_capacity",
      },
    },
  },
  "opt_parser_ignore_zero_capacity": {
   "files": FULL_DATASET["octopus_1hour"],
   "iterations": 5,
   "tests": {
     "all_arcs": {
       "implementation": "f_parser_unoptimised",
     },
     "ignore_zero_cap": {
       "implementation": "f_parser_ignore_zero_capacity",
     },
   },
  },
 
  ### Compiler comparisons
  ## My implementations
  "compilers_ap": {
    "files": FULL_DATASET["octopus_1hour"],
    "iterations": 5,              
    "tests": compilerTests({"ap": {"implementation": "f_ap_latest"}},
                           COMPILERS.keys())
  },
  "compilers_cc": {
    "files": FULL_DATASET["octopus_1hour"],
    "iterations": 5,              
    "tests": compilerTests({"cc": {"implementation": "f_cc_latest"}},
                           COMPILERS.keys())
  },
  "compilers_cs": {
    "files": FULL_DATASET["octopus_1hour"],
    "iterations": 5,              
    "tests": compilerTests({"cs": {"implementation": "f_cs_latest"}},
                           COMPILERS.keys())
  },
  "compilers_relax": {
    "files": FULL_DATASET["octopus_1hour"],
    "iterations": 5,              
    "tests": compilerTests({"relax": {"implementation": "f_relax_latest"}},
                           COMPILERS.keys())
  },
  ## Reference implementations
  "compilers_cs_goldberg": {
    "files": FULL_DATASET["octopus_1hour"],
    "iterations": 5,              
    "tests": compilerTests({"goldberg": {"implementation": "f_cs_goldberg"}},
                           COMPILERS.keys())
  },
  "compilers_relax_frangioni": {
    "files": FULL_DATASET["octopus_1hour"],
    "iterations": 5,              
    "tests": compilerTests({"frangioni": {"implementation": "f_relax_frangioni"}},
                           COMPILERS.keys())
  },
}

INCREMENTAL_TESTS_OFFLINE = {
  # For testing benchmark suite only.
  "development_only": {
    "files": INCREMENTAL_DATASET["development_only"],
    "iterations": 3,
    "tests": {
      "my": {
        "implementation": "i_ap_latest",
      },
      "goldberg": {
        "implementation": "f_cs_goldberg",
      },
    },
  },
                            
  # 
  "incremental_vs_cs": {
    "files": INCREMENTAL_DATASET["google_small_trace_truncated"],
    "iterations": 10,
    "tests": {
      "my_incremental": {
        "implementation": "i_ap_latest",
      },
      "my_costscaling": {
        "implementation": "f_cs_latest",
      },
      "goldberg": {
        "implementation": "f_cs_goldberg",
      },
    },
  },
  "relaxfi_vs_best": {
    "files": INCREMENTAL_DATASET["google_small_trace_truncated"],
    "iterations": 5,
    "tests": {
      "relaxfi": {
        "implementation": "i_relaxf_latest",
        "arguments": [] 
      },
      "goldberg": {
        "implementation": "f_cs_goldberg",
        "arguments": []
      },
    },
  },
}

### Incremental tests: available either as hybrid, or pure online

COST_MODELS = {
               "trivial": 0,
               "random": 1,
               "sjf": 2,
               "quincy": 3,
               "whare": 4,
               "coco": 5,
               "octopus": 6
}

DEFAULT_COST_MODEL = "octopus"
DEFAULT_BATCH_STEP = 10 # microseconds
DEFAULT_ONLINE_FACTOR = 1
DEFAULT_ONLINE_MAX_TIME = 5 # seconds

INCREMENTAL_TESTS_ANYONLINE = {
  # Testing benchmark suite only.
  "development_only": {
    "traces": [
      {
       "name": "tiny_trace",
       "runtime": RUNTIME_MAX
      },
    ],
    "iterations": 3,
    "tests": {
      "my": {
        "implementation": "i_ap_latest",
        "arguments": [],
      },
      "goldberg": {
        "implementation": "f_cs_goldberg",
        "arguments": [],
      },
    },
   },
   "debug_firmament": {
    "traces": [
      {
       "name": "small_trace",
       "scheduling_rounds": 100,
       "percentage": 1,
      }
    ],
    "iterations": 5,
    "tests": {
      "full": { "implementation": "f_cs_goldberg" },
    },
  },
  "generate_dataset_small": {
    "traces": [
      {
       "name": "small_trace",
       "runtime": absoluteRuntime(3600), # run for an hour
       "percentage": 1,
      }
    ],
    "iterations": 0,
    "tests": {
      "goldberg": { "implementation": "f_cs_goldberg" },
    },
  },
  "generate_dataset_medium": {
    "traces": [
      {
       "name": "small_trace",
       "runtime": absoluteRuntime(3600), # run for an hour
       "percentage": 10,
      }
    ],
    "iterations": 0,
    "tests": {
      "goldberg": { "implementation": "f_cs_goldberg" },
    },
  },
  "generate_dataset_large": {
    "traces": [
      {
       "name": "small_trace",
       "runtime": absoluteRuntime(3600), # run for an hour
      }
    ],
    "iterations": 0,
    "tests": {
      "goldberg": { "implementation": "f_cs_goldberg" },
    },
  },
  # Run optimized implementation on whole trace. Get an idea for how fast
  # we can get through it. 
  "how_long_can_we_go": {
    "traces": [
      {
       "name": "google_trace",
      }
    ],
    "iterations": 1,
    "tests": {
      "i_relaxf":    { "implementation": "i_relaxf_latest" },
    },
  },                          
  ### Self comparisons
  ### How does the performance of an incremental solver compare to using the
  ### same solver in a non-incremental mode? Similarly, what proportion of work
  ### must the incremental solver do?
  "same_ap": {
    # Augmenting path is slow. Give it a small dataset.
    "traces": [
      {
       "name": "small_trace",
       "scheduling_rounds": 50,
       "percentage": 1
      }
    ],
    "iterations": 5,
    "tests": {
      "full":           { "implementation": "f_ap_latest" },
      "incremental":    { "implementation": "i_ap_latest" },
    },
  },
  "same_relax": {
    # This implementation of RELAX is 4-5x faster than augmenting path.
    # But still too slow for a large dataset.
    "traces": [
      {
       "name": "small_trace",
       "scheduling_rounds": 50,
       "percentage": 1
      }
    ],
    "iterations": 5,
    "tests": {
      "full":           { "implementation": "f_relax_latest" },
      "incremental":    { "implementation": "i_relax_latest" },
    },
  },
  "same_relaxf": {
    # This is the optimised version of RELAX. Give it a full-size dataset.
    "traces": [
      {
       "name": "small_trace",
       "scheduling_rounds": 100,
      }
    ],
    "iterations": 5,
    "tests": {
      "full":           { "implementation": "f_relax_frangioni" },
      "incremental":    { "implementation": "i_relaxf_latest" },
    },
  },
  
  ### Comparisons between types
  # Evaluation against the best of my (unoptimized) implementations.
  "head_to_head_my": {
    # Give them a small dataset
    "traces": [
      {
       "name": "small_trace",
       "scheduling_rounds": 50,
       "percentage": 1
      }
    ],
    "iterations": 5,
    "tests": {
      "full":           { "implementation": "f_cs_latest" },
      "incremental":    { "implementation": "i_relax_latest" },
    }
  },
  # Fight against the best optimized implementations.
  # Goldberg for full solver, modified RelaxIV for incremental solver.
  "head_to_head_optimised": {
    # These implementations can handle a full-size dataset
    "traces": [
      {
       "name": "google_trace",
      }
    ],
    "iterations": 5,
    "tests": {
      "full":           { "implementation": "f_cs_goldberg" },
      "incremental":    { "implementation": "i_relaxf_latest" },
    },
  },
  "head_to_head_optimised_short": {
    "traces": [
      {
       "name": "small_trace",
       "scheduling_rounds": 100,
      }
    ],
    "iterations": 5,
    "tests": {
      "full":           { "implementation": "f_cs_goldberg" },
      "incremental":    { "implementation": "i_relaxf_latest" },
    },
  },
  "head_to_head_optimised_very_short": {
    "traces": [
      {
       "name": "small_trace",
       "scheduling_rounds": 100,
       "percentage": 1,
      }
    ],
    "iterations": 5,
    "tests": {
      "full":           { "implementation": "f_cs_goldberg" },
      "incremental":    { "implementation": "i_relaxf_latest" },
    },
  },                                  
}

INCREMENTAL_TESTS_HYBRID = INCREMENTAL_TESTS_ANYONLINE.copy()
INCREMENTAL_TESTS_ONLINE = INCREMENTAL_TESTS_ANYONLINE.copy()

TESTS = mergeDicts(
  [FULL_TESTS, 
   INCREMENTAL_TESTS_OFFLINE, 
   INCREMENTAL_TESTS_HYBRID,
   INCREMENTAL_TESTS_ONLINE], 
  ["f", "iof", "ihy", "ion"],
  ["full", "incremental_offline", "incremental_hybrid", "incremental_online"])