// TEST: include_limits
// DESCRIPTION: Include limits.h and check INT_MAX
// EXPECTED_EXIT: 1
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 5.2.4.2.1 (Sizes of integer types)

#include <limits.h>

int main(void) {
    return INT_MAX > 0;
}
