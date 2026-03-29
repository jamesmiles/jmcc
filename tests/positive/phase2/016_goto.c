// TEST: goto_stmt
// DESCRIPTION: Goto statement with label
// EXPECTED_EXIT: 42
// ENVIRONMENT: hosted
// PHASE: 2
// STANDARD_REF: 6.8.6.1 (The goto statement)

int main(void) {
    goto end;
    return 0;
end:
    return 42;
}
