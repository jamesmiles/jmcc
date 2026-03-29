// TEST: typedef_basic
// DESCRIPTION: Basic typedef for int type
// EXPECTED_EXIT: 42
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.7.8 (Type definitions)

typedef int myint;

int main(void) {
    myint x = 42;
    return x;
}
