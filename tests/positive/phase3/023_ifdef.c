// TEST: ifdef
// DESCRIPTION: Conditional compilation with #ifdef
// EXPECTED_EXIT: 1
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.10.1 (Conditional inclusion)

#define FEATURE_X

int main(void) {
#ifdef FEATURE_X
    return 1;
#else
    return 0;
#endif
}
