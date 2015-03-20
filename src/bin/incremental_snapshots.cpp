/* Parses a standard DIMACS input file, solves the min-cost flow problem.
 * Parses an extended DIMACS input file specifying change(s) to the graph,
 * and solves it using an incremental approach. Outputs DIMACS representation
 * of the solution. */

#include "augmenting_path.h"

#include <iostream>
#include <fstream>
#include <string>

#include <boost/program_options.hpp>
#include <boost/timer/timer.hpp>
#include <glog/logging.h>

#include "residual_network.h"
#include "dynamic_maintain_optimality.h"
#include "dimacs.h"

#define TIMER_FORMAT "ALGOTIME: %w\n"

using namespace flowsolver;

void exportGraph(DIMACSExporter<ResidualNetwork> &exporter) {
	exporter.write();
	std::cout << "c EOI" << std::endl;
	std::cout.flush();
}

int main(int, char *argv[]) {
	FLAGS_logtostderr = true;
	google::InitGoogleLogging(argv[0]);

	// load full file
	ResidualNetwork *g = DIMACSIncrementalFullImporter<ResidualNetwork>
                                                              (std::cin).read();

	// re-export immediately: this is our initial snapshot
	DIMACSExporter<ResidualNetwork> exporter(*g, std::cout);
	exportGraph(exporter);

	// now process stream of incremental deltas, outputting snapshots
	DIMACSIncrementalDeltaImporter<ResidualNetwork>
	                                           incremental_importer(std::cin, *g);

	while (incremental_importer.read()) {
		exportGraph(exporter);
	}

	return 0;
}