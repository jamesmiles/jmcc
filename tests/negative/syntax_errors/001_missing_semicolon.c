// TEST: missing_semicolon
// DESCRIPTION: Missing semicolon after return statement
// EXPECT_COMPILE_FAIL: yes
// ERROR_PATTERN: expected ';'
// PHASE: 1

int main(void) {
    return 0
}
