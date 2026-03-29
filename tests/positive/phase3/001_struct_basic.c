// TEST: struct_basic
// DESCRIPTION: Basic struct declaration and member access
// EXPECTED_EXIT: 30
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.7.2.1 (Structure and union specifiers)

struct Point {
    int x;
    int y;
};

int main(void) {
    struct Point p;
    p.x = 10;
    p.y = 20;
    return p.x + p.y;
}
