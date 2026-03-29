// TEST: enum_basic
// DESCRIPTION: Basic enum declaration and use
// EXPECTED_EXIT: 2
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.7.2.2 (Enumeration specifiers)

enum Color {
    RED,
    GREEN,
    BLUE
};

int main(void) {
    enum Color c = BLUE;
    return c;
}
