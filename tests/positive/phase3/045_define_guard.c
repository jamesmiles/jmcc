// TEST: define_guard
// DESCRIPTION: Include guard pattern with #ifndef/#define/#endif
// EXPECTED_EXIT: 42
// ENVIRONMENT: hosted
// PHASE: 3

#ifndef MY_CONSTANT
#define MY_CONSTANT 42
#endif

#ifndef MY_CONSTANT
#define MY_CONSTANT 99
#endif

int main(void) {
    return MY_CONSTANT;
}
