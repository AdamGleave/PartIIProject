/*
 * ResidualNetworkUtil.cpp
 *
 *  Created on: 18 Dec 2014
 *      Author: adam
 */

#include <cassert>
#include <queue>

#include "ResidualNetworkUtil.h"

namespace flowsolver {

uint64_t ResidualNetworkUtil::augmentingFlow(std::queue<Arc *> path) {
	uint64_t augmenting_flow = UINT64_MAX;

	while (!path.empty()) {
		Arc *arc = path.front();
		path.pop();

		uint64_t capacity = arc->getCapacity();
		augmenting_flow = std::min(augmenting_flow, capacity);
	}

	return augmenting_flow;
}

void ResidualNetworkUtil::pushFlow
 	 	 (ResidualNetwork &g, std::queue<Arc *> path, uint64_t flow) {
	while (!path.empty()) {
		Arc *arc = path.front();
		path.pop();

		uint32_t src = arc->getSrcId();
		uint32_t dst = arc->getDstId();
		// N.B. Must do this through ResidualNetwork rather than Arc
		// directly, so that reverse arc is also updated
		g.pushFlow(src, dst, flow);
	}
}

void ResidualNetworkUtil::augmentPath
	 	 	 	 	 	  (ResidualNetwork &g, std::queue<Arc *> path) {
	uint32_t source_id = path.front()->getSrcId();
	int64_t supply = g.getBalance(source_id);
	uint32_t sink_id = path.back()->getDstId();
	int64_t demand = -g.getBalance(sink_id);
	int64_t supply_limit = std::min(demand, supply);
	assert(supply_limit >= 0);

	uint64_t flow = std::min((uint64_t)supply_limit, augmentingFlow(path));
	pushFlow(g, path, flow);
}

void ResidualNetworkUtil::cancelCycle
						  (ResidualNetwork &g, std::queue<Arc *> path) {
	uint64_t flow = augmentingFlow(path);
	pushFlow(g, path, flow);
}

} /* namespace flowsolver */
