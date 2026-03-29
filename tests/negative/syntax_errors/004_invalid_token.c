// TEST: invalid_token
// DESCRIPTION: Invalid character in source
// EXPECT_COMPILE_FAIL: yes
// ERROR_PATTERN: unexpected character
// PHASE: 1

int main(void) {
    return @;
}
