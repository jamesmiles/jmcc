// TEST: global_var
// DESCRIPTION: Global variable declaration and use
// EXPECTED_EXIT: 42
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.7.9 (Initialization), 6.2.2 (Linkages of identifiers)

int x = 42;

int main(void) {
    return x;
}
