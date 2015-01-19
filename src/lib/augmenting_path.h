#ifndef LIB_AUGMENTING_PATH_H_
#define LIB_AUGMENTING_PATH_H_

#include <climits>
#include <vector>
#include <queue>

#include "residual_network.h"

namespace flowsolver {

class AugmentingPath {
	ResidualNetwork &g;
	std::vector<uint64_t> potentials;
	const uint32_t num_nodes;

public:
	AugmentingPath(ResidualNetwork &g);
	// returns true if feasible solution exists, and updates g accordingly;
	// false if no feasible solution, g left in undefined state
	std::queue<Arc *> predecessorPath(uint32_t source, uint32_t sink,
																					const std::vector<uint32_t>& parents);
	void run();
	virtual ~AugmentingPath();
};

} /* namespace flowsolver */

#endif /* LIB_AUGMENTING_PATH_H_ */