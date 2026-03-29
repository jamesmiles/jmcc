// TEST: unclosed_comment
// DESCRIPTION: Unterminated block comment should fail
// EXPECT_COMPILE_FAIL: yes
// ERROR_PATTERN: unterminated block comment
// PHASE: 1

int main(void) {
    /* this comment never ends
    return 0;
}
