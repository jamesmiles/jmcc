// TEST: pointer_write
// DESCRIPTION: Write through a pointer
// EXPECTED_EXIT: 99
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.5.3.2 (Address and indirection operators)

int main(void) {
    int x = 0;
    int *p = &x;
    *p = 99;
    return x;
}
