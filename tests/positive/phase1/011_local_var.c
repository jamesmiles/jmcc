// TEST: local_var
// DESCRIPTION: Declare and use a local variable
// EXPECTED_EXIT: 10
// ENVIRONMENT: hosted
// PHASE: 1
// STANDARD_REF: 6.7 (Declarations)

int main(void) {
    int x = 10;
    return x;
}
