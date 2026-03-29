// TEST: ifndef
// DESCRIPTION: Conditional compilation with #ifndef
// EXPECTED_EXIT: 2
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.10.1 (Conditional inclusion)

int main(void) {
#ifndef UNDEFINED_MACRO
    return 2;
#else
    return 0;
#endif
}
