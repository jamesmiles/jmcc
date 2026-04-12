#ifndef SIM_API_H
#define SIM_API_H

// This header depends on sim_begin.h being included first
// (simulating SDL's begin_code.h / DECLSPEC pattern)
#ifndef SIM_VALUE
#error "sim_begin.h must be included before sim_api.h"
#endif

static inline int sim_add(int a, int b) { return a + b; }

#endif
