// TEST: undeclared_var
// DESCRIPTION: Use of undeclared variable
// EXPECT_COMPILE_FAIL: yes
// ERROR_PATTERN: undeclared variable
// PHASE: 1

int main(void) {
    return x;
}
