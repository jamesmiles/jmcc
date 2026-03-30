// TEST: sizeof_expr
// DESCRIPTION: sizeof applied to expressions
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int main(void) {
    int x = 42;
    char c = 'a';
    int *p = &x;
    if (sizeof(x) != 4) return 1;
    if (sizeof(c) != 1) return 2;
    if (sizeof(p) != 8) return 3;
    if (sizeof(x + 1) != 4) return 4;
    return 0;
}
