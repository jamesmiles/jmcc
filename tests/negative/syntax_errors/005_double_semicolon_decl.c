// TEST: unclosed_string
// DESCRIPTION: Unterminated string literal should fail
// EXPECT_COMPILE_FAIL: yes
// ERROR_PATTERN: unterminated string
// PHASE: 1

int main(void) {
    char *s = "hello;
    return 0;
}
