import os
from enum import Enum

from config.common import *
from visualisation.test_types import FigureTypes

def dictFilter(d):
  return lambda k : d[k]

def updateFiguresWithTypes(d, types):
  res = {}
  for type_name, (preconditions, type) in types.items():
    d_for_type = {}
    for k, v in d.items():
      preconditions_satisfied = all([p in v for p in preconditions])
      if preconditions_satisfied:
        v = v.copy()
        v.update({'type': type})
        d_for_type[k + '_' + type_name] = v 
    res.update(d_for_type)
  return res


### Miscellaneous settings
CONFIDENCE_LEVEL = 0.95

### Paths

DOC_PREFIX = "doc"
DATA_PREFIX = "data"
FIGURE_PREFIX = "figures"
DOC_ROOT = os.path.join(PROJECT_ROOT, DOC_PREFIX)
DATA_ROOT = os.path.join(DOC_ROOT, DATA_PREFIX)
FIGURE_ROOT = os.path.join(DOC_ROOT, FIGURE_PREFIX)

### Compiler test cases

FULL_FILE_FILTER = dictFilter({
  'clusters/natural/google_trace/octopus/1hour/full_size.min': 'Warehouse Scale',
  'clusters/natural/google_trace/octopus/1hour/large.min': 'Large',
  'clusters/natural/google_trace/octopus/1hour/medium.min': 'Medium',
  'clusters/natural/google_trace/octopus/1hour/small.min': 'Small',
})

FULL_DATASETS = ['Small', 'Medium', 'Large', 'Warehouse Scale']

COMPILER_IMPLEMENTATIONS_FULL = {
  'clang_debug': 'Clang Debug',
  'clang_O0': 'Clang Unoptimised',
  'clang_O1': 'Clang O1',
  'clang_O2': 'Clang O2',
  'clang_O3': 'Clang O3',
  'gcc_debug': 'GCC Debug',
  'gcc_O0': 'GCC Unoptimised',
  'gcc_O1': 'GCC O1',
  'gcc_O2': 'GCC O2',
  'gcc_O3': 'GCC O3',
}

COMPILER_IMPLEMENTATIONS_DEFAULT = ['clang_O2', 'clang_O3', 'gcc_O2', 'gcc_O3']

COMPILER_IMPLEMENTATIONS_COLORS = {
  'Clang O2': 'r',
  'Clang O3': 'g',
  'GCC O2': 'b',
  'GCC O3': 'k',
}

def compiler_implementations(l, name):
  return {name + '_' + k : v if k in l else None 
          for k, v in COMPILER_IMPLEMENTATIONS_FULL.items()}

# TODO: datasets, implementations, colours?
# TODO: baseline doesn't really make sense, maybe need new class
COMPILER_FIGURES = {
  'ap': {
    'data': 'f_compilers_ap',
    'datasets': ['Small', 'Medium']
  },
  'cc': {
    'data': 'f_compilers_cc',
    'datasets': ['Small', 'Medium']
  },
  'cs': {
    'data': 'f_compilers_cs',
    'datasets': ['Large', 'Warehouse Scale']
  },
  'relax': {
    'data': 'f_compilers_relax',
    'datasets': ['Small']
  },
  # others implementations
  'goldberg': {
    'data': 'f_compilers_cs_goldberg',
    'datasets': ['Large', 'Warehouse Scale']
  },       
  'frangioni': {
    'data': 'f_compilers_relax_frangioni',
    'datasets': ['Medium', 'Large']
  },
}

def apply_compiler_defaults(d):
  for k, v in d.items():
    if 'file_filter' not in v:
      v['file_filter'] = FULL_FILE_FILTER
      if 'datasets' not in v:
        v['datasets'] = FULL_DATASETS
    if 'test_filter' not in v:
      filter_dict = compiler_implementations(COMPILER_IMPLEMENTATIONS_DEFAULT, k)
      v['test_filter'] = dictFilter(filter_dict)
      assert('implementations' not in v)
      v['implementations'] = [COMPILER_IMPLEMENTATIONS_FULL[k] 
                              for k in COMPILER_IMPLEMENTATIONS_DEFAULT]
      v['colours'] = COMPILER_IMPLEMENTATIONS_COLORS
      
apply_compiler_defaults(COMPILER_FIGURES)

def updateCompilerFigures(d):
  types = {'absolute': ([], FigureTypes.optimisation_absolute)}
  return updateFiguresWithTypes(d, types)

COMPILER_FIGURES = updateCompilerFigures(COMPILER_FIGURES)

### Optimisation figures

OPTIMISATION_FIGURES = {
  ### Optimisations
  ## Augmenting path
  'ap_big_vs_small': {
    'data': 'f_opt_ap_big_vs_small_heap',
    'file_filter': FULL_FILE_FILTER,
    'test_filter': dictFilter({
      'big': 'Big Heap',
      'small_vector': 'Small Heap',
      'small_map': None
    }),
    
    'datasets': ['Small', 'Medium'],
    'implementations': ['Big Heap', 'Small Heap'],
    'baseline': 'Big Heap',
    'colours': {
      'Big Heap': 'r',
      'Small Heap': 'b',
    }
  },                      
}

def updateOptimisationFigures(d):
  types = {'absolute': ([], FigureTypes.optimisation_absolute),
           'relative': ([], FigureTypes.optimisation_relative)}
  return updateFiguresWithTypes(d, types)

OPTIMISATION_FIGURES = updateOptimisationFigures(OPTIMISATION_FIGURES)

### Incremental test cases

# Time, in seconds, *after* proper start of cluster.
# So 600s would be after time 12,000,000,000 in cluster.
DEFAULT_INCREMENTAL_START = 600

# Number of elements to include in moving average (for incremental_over_time)
DEFAULT_WINDOW_SIZE = 100

INCREMENTAL_TEST_FILTER = dictFilter({
  'full': 'Standard',
  'incremental': 'Incremental',
})

INCREMENTAL_FIGURES = {
  'optimised': {
    'data': 'ion_head_to_head_optimised',
    'type': FigureTypes.incremental_cdf,
    'test_filter': INCREMENTAL_TEST_FILTER,
    
    'trace': 'full_size',
    'implementations': ['Standard', 'Incremental'],
    'colours': {
      'Standard': 'r',
      'Incremental': 'b',
    }
  },
} 

def updateIncrementalFigures(d):
  types = {'cdf': ([], FigureTypes.incremental_cdf),
           'hist': ([], FigureTypes.incremental_hist),
           'over_time': ([], FigureTypes.incremental_over_time)}
  return updateFiguresWithTypes(d, types)

INCREMENTAL_FIGURES = updateIncrementalFigures(INCREMENTAL_FIGURES)

### Approximate test cases
APPROXIMATE_ACCURACY_THRESHOLD = 90 # percent
APPROXIMATE_NUM_BINS = 10

APPROXIMATE_MAX_COST_PARAMETER = 0.05
APPROXIMATE_MAX_TASK_ASSIGNMENTS_PARAMETER = 20

APPROXIMATE_DEFAULT_PERCENTILES = {
  1: '$1^{\mathrm{st}}$ percentile', 
  5: '$5^{\mathrm{th}}$ percentile',
  25: '$25^{\mathrm{th}}$ percentile',
  50: 'Median',
}

APPROXIMATE_FIGURES = {
  'road': {
    'data': 'af_road',
    
    # Used by oracle policy
    #'min_accuracy': can be used to override APPROXIMATE_ACCURACY_THRESHOLD
    
    # Used by policy accuracy-parameter plot, policy error and speed CDF generators 
    'condition': 'cost', # or 'task_assignments'
    
    # Used by policy accuracy-parameter plot
    #'max_cost_parameter': can be used to override APPROXIMATE_MAX_COST_PARAMETER
    #'max_task_assignments_parameter': can be used to override APPROXIMATE_MAX_TASK_ASSIGNMENTS_PARAMETER
    #'percentiles': can be used to override APPROXIMATE_DEFAULT_PERCENTILES
    
    # Used by policy error and speed CDF generators
    'heuristic_parameter': 0.025, # threshold used by heuristic
    'target_accuracy': 99, # in percent. Used for comparison
    
    # Used by over_time generator only
    'file': 'general/natural/road/road_flow_03_NH_e.min',
  }
}

def updateApproximateFigures(d):
  types = {'oracle_policy': ([], FigureTypes.approximate_oracle_policy),
               'policy_parameter_accuracy': (['condition'], FigureTypes.approximate_policy_accuracy),
               'policy_error_cdf': (['condition', 'heuristic_parameter', 'target_accuracy'],
                                    FigureTypes.approximate_error_cdf),
               'policy_speed_cdf': (['condition', 'heuristic_parameter', 'target_accuracy'],
                                    FigureTypes.approximate_speed_cdf),
               'over_time': (['file'], FigureTypes.approximate_cost_vs_time)}
  return updateFiguresWithTypes(d, types)
  
APPROXIMATE_FIGURES = updateApproximateFigures(APPROXIMATE_FIGURES)

# APPROXIMATE_FIGURES = {
#   'road_oracle_policy': {
#     'data': 'af_road',
#     'type': FigureTypes.approximate_oracle_policy,
#     
#     #'min_accuracy': 90 # in percent -- defaults to APPROXIMATE_ACCURACY_THRESHOLD 
#   },
#   'road_policy_accuracy': {
#     'data': 'af_road',
#     'type': FigureTypes.approximate_policy_accuracy,
#     
#     #'min_accuracy': 90 # in percent -- defaults to APPROXIMATE_ACCURACY_THRESHOLD
#     'condition': 'cost', # or 'task_assignments'
#     #'max_cost_parameter': 0.05, # defaults to APPROXIMATE_MAX_COST_PARAMETER
#     #'max_task_assignments_parameter': 20, # defaults to APPROXIMATE_MAX_TASK_ASSIGNMENTS_PARAMETER
#     'percentiles': [1, 5, 25, 50],
#     'labels': ['$1^{\mathrm{st}}$ percentile', '$5^{\mathrm{th}}$ percentile',
#                '$25^{\mathrm{th}}$ percentile', 'Median']
#   },
#   'road_policy_error_cdf': {
#     'data': 'af_road',
#     'type': FigureTypes.approximate_error_cdf,
#     
#     #'min_accuracy': 90 # in percent -- defaults to APPROXIMATE_ACCURACY_THRESHOLD
#     'condition': 'cost', # or 'task_assignments'
#     'heuristic_parameter': 0.025, # threshold used by heuristic
#     'target_accuracy': 99 # in percent. Used for comparison
#   },
#   'road_policy_speed_cdf': {
#     'data': 'af_road',
#     'type': FigureTypes.approximate_speed_cdf,
#     
#     #'min_accuracy': 90 # in percent -- defaults to APPROXIMATE_ACCURACY_THRESHOLD
#     'condition': 'cost', # or 'task_assignments'
#     'heuristic_parameter': 0.025, # threshold used by heuristic
#     'target_accuracy': 99 # in percent. Used for comparison with oracle model
#   },
#   'road_cost_vs_time': {
#     'data': 'af_road',
#     'type': FigureTypes.approximate_cost_vs_time,
#     
#     'file': 'general/natural/road/road_flow_03_NH_e.min',
#   }                      
# }

### All figures

FIGURES = mergeDicts([OPTIMISATION_FIGURES,
                      COMPILER_FIGURES,
                      INCREMENTAL_FIGURES,
                      APPROXIMATE_FIGURES],
                     ["opt", 'com', "inc", "app"])