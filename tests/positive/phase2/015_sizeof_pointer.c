// TEST: sizeof_pointer
// DESCRIPTION: sizeof(int*) is 8 on x86-64
// EXPECTED_EXIT: 8
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.5.3.4 (The sizeof and _Alignof operators)

int main(void) {
    return sizeof(int *);
}
