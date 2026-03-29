// TEST: assign_to_literal
// DESCRIPTION: Cannot assign to a literal value
// EXPECT_COMPILE_FAIL: yes
// ERROR_PATTERN: not an lvalue
// PHASE: 1

int main(void) {
    5 = 10;
    return 0;
}
