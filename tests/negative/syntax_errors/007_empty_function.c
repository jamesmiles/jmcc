// TEST: missing_return_type
// DESCRIPTION: Function without a return type should fail
// EXPECT_COMPILE_FAIL: yes
// ERROR_PATTERN: expected declaration
// PHASE: 1

main(void) {
    return 0;
}
