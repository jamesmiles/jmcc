// TEST: string_literal
// DESCRIPTION: String literal stored in rodata and accessed as char*
// EXPECTED_EXIT: 72
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.4.5 (String literals)

int main(void) {
    char *s = "Hello";
    return s[0];
}
