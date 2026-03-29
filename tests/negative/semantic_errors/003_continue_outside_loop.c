// TEST: continue_outside_loop
// DESCRIPTION: Continue statement outside loop should fail
// EXPECT_COMPILE_FAIL: yes
// ERROR_PATTERN: continue outside
// PHASE: 1

int main(void) {
    continue;
    return 0;
}
