// TEST: missing_paren
// DESCRIPTION: Missing closing parenthesis
// EXPECT_COMPILE_FAIL: yes
// ERROR_PATTERN: expected ')'
// PHASE: 1

int main(void {
    return 0;
}
