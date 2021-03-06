/* Parses DIMACS input. Runs a minimum-cost maximum-flow algorithm,
 * outputting a DIMACS representation of the solution. */

#include "augmenting_path.h"
#include "cost_scaling.h"
#include "cycle_cancelling.h"
#include "relax.h"

#include <cstdint>
#include <iostream>
#include <map>
#include <string>
#include <vector>

#include <boost/program_options.hpp>
#include <boost/timer/timer.hpp>
#include <glog/logging.h>

#include "flow_network.h"
#include "residual_network.h"
#include "dimacs.h"

#define TIMER_FORMAT "ALGOTIME: %w\n"

using namespace flowsolver;

int main(int argc, char *argv[]) {
	// for timing algorithms
	boost::timer::auto_cpu_timer t(std::cerr, TIMER_FORMAT);
	t.stop();

	// inspiration for this style of command parsing:
	// http://stackoverflow.com/questions/15541498/how-to-implement-subcommands-using-boost-program-options
	namespace po = boost::program_options;

	po::options_description global("Global options");
	global.add_options()
			("help", "produce help message")
			("flow", po::value<bool>()->default_value(true), "Output flow solution.")
			("quiet", po::bool_switch()->default_value(false),
			 "Suppress all but the highest priority logging messages.")
			("command", po::value<std::string>(), "command to execute")
			("subargs", po::value<std::vector<std::string> >(), "Arguments for command");

	po::positional_options_description pos;
	pos.add("command", 1).
			add("subargs", -1);

	po::variables_map vm;

	po::parsed_options parsed = po::command_line_parser(argc, argv).
			options(global).
			positional(pos).
			allow_unregistered().
			run();

	po::store(parsed, vm);

	std::string usage = "usage: " + std::string(argv[0])
						+ " <augmenting_path|cost_scaling|cycle_cancelling>"
						+	" <subcommand arguments>";
	if (!vm.count("command")) {
		std::cerr << "must specify command" << std::endl;
		std::cerr << usage << std::endl;
		return -1;
	}
	std::string cmd = vm["command"].as<std::string>();

	bool flow = vm["flow"].as<bool>();
	bool quiet = vm["quiet"].as<bool>();

	// initialise logging
	FLAGS_logtostderr = true;
	if (quiet) {
		FLAGS_minloglevel = google::ERROR;
	}
	google::InitGoogleLogging(argv[0]);

	// Collect all the unrecognized options from the first pass. This will include the
	// (positional) command name, so we need to erase that.
	std::vector<std::string> opts = po::collect_unrecognized(parsed.options, po::include_positional);
	opts.erase(opts.begin());

	// match on command names
	if (cmd == "augmenting_path") {
		// augmenting_path command has no options
		po::options_description desc("augmenting path options");
		po::store(po::command_line_parser(opts).options(desc).run(), vm);

		ResidualNetwork *g = DIMACSOriginalImporter<ResidualNetwork>(std::cin).read();
		t.start();
		AugmentingPath ap(*g);
		ap.run();
		t.stop();
		t.report();
		if (flow) {
			DIMACSExporter<ResidualNetwork>(*g, std::cout).writeFlow();
		}

		return 0;
	} else if (cmd == "cost_scaling")
	{
		// cost_scaling command options
		po::options_description desc("cost scaling options");
		desc.add_options()
			("help", "produce help message")
			("forbid-antiparallel-arcs", "do not allow an arc to be defined from src->dst and dst->src")
			("permit-duplicate-arcs", "allow multiple arcs between two nodes")
			("scaling-factor", po::value<uint32_t>(), "factor by which to divide epsilon on each iteration")
			("statistics", po::value<std::string>(), "output statistics on each iteration to CSV file specified")
			("scheduling-graph", "Flag used in conjunction with -statistics. Is the input network produced by a flow scheduler? If so, the number of task assignments modified is computed.")
			("epsilon", po::value<double>(), "threshold for epsilon-optimality")
			("iterations", po::value<uint64_t>(), "threshold for number of iterations")
			("cost-threshold", po::value<double>(), "minimum factor cost reduced by between iterations")
			("task-assignments", po::value<uint32_t>(), "minimum number of task assignments changed between iterations");
		po::store(po::command_line_parser(opts).options(desc).run(), vm);

		if (vm.count("help")) {
			std::cout << desc << std::endl;
			return 0;
		}

		if (vm.count("statistics") + vm.count("epsilon") + vm.count("iterations")
				+ vm.count("cost-threshold") + vm.count("task-assignments") > 1) {
			throw po::invalid_option_value("at most one of --statistics, --epsilon, "
							"--iterations and --cost-threshold can be used");
		}

		bool forbid_antiparallel_arcs = vm.count("forbid-antiparallel-arcs");
		bool allow_duplicate_arcs = vm.count("permit-duplicate-arcs");
		FlowNetwork *g = DIMACSOriginalImporter<FlowNetwork>(std::cin,
				                !forbid_antiparallel_arcs, allow_duplicate_arcs).read();
		CostScaling *cs;

		t.start();
		if (vm.count("scaling-factor")) {
			uint32_t scaling_factor = vm["scaling-factor"].as<uint32_t>();
			cs = new CostScaling(*g, scaling_factor);
		} else {
			cs = new CostScaling(*g);
		}
		bool success;

		if (vm.count("statistics")) {
			std::string path = vm["statistics"].as<std::string>();
			bool scheduling_graph = vm.count("scheduling-graph");
			success = cs->runStatistics(path, scheduling_graph);
		} else if (vm.count("epsilon")) {
			double threshold = vm["epsilon"].as<double>();
			success = cs->runEpsilonOptimal(threshold);
		} else if (vm.count("iterations")) {
			uint64_t max_iterations = vm["iterations"].as<uint64_t>();
			success = cs->runFixedIterations(max_iterations);
		} else if (vm.count("cost-threshold")) {
			double min_factor = vm["cost-threshold"].as<double>();
			success = cs->runCostThreshold(min_factor);
		} else if (vm.count("task-assignments")) {
			uint32_t min_assignments = vm["task-assignments"].as<uint32_t>();
			success = cs->runTaskAssignmentThreshold(min_assignments);
		} else {
			success = cs->runOptimal();
		}

		t.stop();
		t.report();
		delete cs;
		LOG_IF(ERROR, !success) << "No feasible solution.";

		if (flow) {
			DIMACSExporter<FlowNetwork>(*g, std::cout).writeFlow();
		}

		return 0;
	} else if (cmd == "cycle_cancelling") {
		// cycle_cancelling command has no options
		po::options_description desc("cycle cancelling options");
		po::store(po::command_line_parser(opts).options(desc).run(), vm);

		ResidualNetwork *g = DIMACSOriginalImporter<ResidualNetwork>(std::cin).read();
		t.start();
		CycleCancelling cc(*g);
		cc.run();
		t.stop();
		t.report();

		if (flow) {
			DIMACSExporter<ResidualNetwork>(*g, std::cout).writeFlow();
		}

		return 0;
	} else if (cmd == "relax") {
		// augmenting_path command has no options
		po::options_description desc("relax options");
		po::store(po::command_line_parser(opts).options(desc).run(), vm);

		ResidualNetwork *g = DIMACSOriginalImporter<ResidualNetwork>(std::cin).read();
		t.start();
		RELAX ap(*g);
		ap.run();
		t.stop();
		t.report();

		if (flow) {
			DIMACSExporter<ResidualNetwork>(*g, std::cout).writeFlow();
		}

		return 0;
	} else {
		// unrecognised command
		std::cerr << "unrecognised command: " << cmd << std::endl;
		std::cerr << usage << std::endl;
		return -1;
	}
}
