// TEST: include_stdbool
// DESCRIPTION: Include stdbool.h and use bool/true/false
// EXPECTED_EXIT: 1
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 7.18 (Boolean type and values)

#include <stdbool.h>

int main(void) {
    bool x = true;
    bool y = false;
    return x && !y;
}
