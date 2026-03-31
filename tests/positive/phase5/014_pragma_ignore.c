// TEST: pragma_ignore
// DESCRIPTION: #pragma interface/implementation should be silently ignored
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: pragma test ok
// ENVIRONMENT: hosted
// PHASE: 5

#pragma interface
#pragma implementation

int printf(const char *fmt, ...);

int main(void) {
    printf("pragma test ok\n");
    return 0;
}
