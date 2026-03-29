// TEST: sizeof_int
// DESCRIPTION: sizeof(int) should be 4 on x86-64
// EXPECTED_EXIT: 4
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.5.3.4 (The sizeof and _Alignof operators)

int main(void) {
    return sizeof(int);
}
