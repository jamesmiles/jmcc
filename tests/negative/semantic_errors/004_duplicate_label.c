// TEST: empty_char
// DESCRIPTION: Empty character literal should fail
// EXPECT_COMPILE_FAIL: yes
// ERROR_PATTERN: empty character
// PHASE: 1

int main(void) {
    char c = '';
    return c;
}
