// TEST: sizeof_char
// DESCRIPTION: sizeof(char) is always 1
// EXPECTED_EXIT: 1
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.5.3.4 (The sizeof and _Alignof operators)

int main(void) {
    return sizeof(char);
}
