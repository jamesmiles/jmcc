// TEST: test130_debug
// DESCRIPTION: 00130 with printf debug
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: arr[1][3]=2
// ENVIRONMENT: hosted
// PHASE: 4
int printf(const char *fmt, ...);
int main(void) {
    char arr[2][4], *q;
    int v[4];
    q = &arr[1][3];
    arr[1][3] = 2;
    v[0] = 2;
    printf("arr[1][3]=%d\n", (int)arr[1][3]);
    return 0;
}
