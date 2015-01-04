/* Parses DIMACS input. Runs a minimum-cost maximum-flow algorithm,
 * outputting a DIMACS representation of the solution. */


#include <cstdint>
#include <iostream>
#include <map>
#include <string>
#include <vector>

#include <boost/program_options.hpp>
#include <glog/logging.h>

#include "CostScaling.h"
#include "CycleCancelling.h"
#include "DIMACS.h"
#include "FlowNetwork.h"
#include "ResidualNetwork.h"

using namespace flowsolver;

int main(int argc, char *argv[]) {
	//google::InitGoogleLogging(argv[0]);

	// inspiration for this style of command parsing:
	// http://stackoverflow.com/questions/15541498/how-to-implement-subcommands-using-boost-program-options
    namespace po = boost::program_options;

    po::options_description global("Global options");
    global.add_options()
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
					+ " <cost_scaling|cycle_cancelling> <subcommand arguments>";
    if (!vm.count("command")) {
    	std::cerr << "must specify command" << std::endl;
    	std::cerr << usage << std::endl;
    	return -1;
    }
    std::string cmd = vm["command"].as<std::string>();

    // Collect all the unrecognized options from the first pass. This will include the
	// (positional) command name, so we need to erase that.
	std::vector<std::string> opts = po::collect_unrecognized(parsed.options, po::include_positional);
	opts.erase(opts.begin());

	// match on command names
    if (cmd == "cycle_cancelling")
    {
        // cycle_cancelling command has no options
    	po::options_description desc("cycle cancelling options");
        po::store(po::command_line_parser(opts).options(desc).run(), vm);

    	ResidualNetwork *g = DIMACS<ResidualNetwork>::readDIMACSMin(std::cin);
    	CycleCancelling cc(*g);
    	cc.run();
    	DIMACS<ResidualNetwork>::writeDIMACSMinFlow(*g, std::cout);

    	return 0;
    }
    else if (cmd == "cost_scaling")
    {
    	// cost_scaling command options
		po::options_description desc("cost scaling options");
		desc.add_options()
			("help", "produce help message")
			("epsilon", po::value<double>(), "threshold for epsilon-optimality")
			("iterations", po::value<uint64_t>(), "threshold for number of iterations");
		po::store(po::command_line_parser(opts).options(desc).run(), vm);

		if (vm.count("help")) {
			std::cout << desc << std::endl;
			return 0;
		}

		if (vm.count("epsilon") + vm.count("iterations") > 1) {
			throw po::invalid_option_value
					  ("at most one of --epsilon and --iterations can be used");
		}

		FlowNetwork *g = DIMACS<FlowNetwork>::readDIMACSMin(std::cin);
		CostScaling cc(*g);
		bool success;

		if (vm.count("epsilon")) {
			double threshold = vm["epsilon"].as<double>();
			success = cc.runEpsilonOptimal(threshold);
		} else if (vm.count("iterations")) {
			uint64_t max_iterations = vm["iterations"].as<uint64_t>();
			success = cc.runFixedIterations(max_iterations);
		} else {
			success = cc.runOptimal();
		}

		LOG_IF(ERROR, !success) << "No feasible solution.";
		DIMACS<FlowNetwork>::writeDIMACSMinFlow(*g, std::cout);

		return 0;
    } else {
    	// unrecognised command
    	std::cerr << "unrecognised command: " << cmd << std::endl;
    	std::cerr << usage << std::endl;
    	return -1;
    }
}
