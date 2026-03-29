// TEST: pointer_basic
// DESCRIPTION: Basic pointer operations (address-of, dereference)
// EXPECTED_EXIT: 42
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.5.3.2 (Address and indirection operators)

int main(void) {
    int x = 42;
    int *p = &x;
    return *p;
}
