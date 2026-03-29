// TEST: break_outside_loop
// DESCRIPTION: Break statement outside loop/switch should fail
// EXPECT_COMPILE_FAIL: yes
// ERROR_PATTERN: break outside
// PHASE: 1

int main(void) {
    break;
    return 0;
}
