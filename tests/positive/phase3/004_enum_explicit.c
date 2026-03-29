// TEST: enum_explicit
// DESCRIPTION: Enum with explicit values
// EXPECTED_EXIT: 30
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.7.2.2 (Enumeration specifiers)

enum Status {
    OK = 10,
    WARN = 20,
    ERR = 30
};

int main(void) {
    return ERR;
}
