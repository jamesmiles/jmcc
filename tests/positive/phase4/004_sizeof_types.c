// TEST: sizeof_types
// DESCRIPTION: sizeof for all basic types
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 1 2 4 8 4 8
// ENVIRONMENT: hosted
// PHASE: 4

int printf(const char *fmt, ...);

int main(void) {
    printf("%d %d %d %d %d %d\n",
        (int)sizeof(char), (int)sizeof(short),
        (int)sizeof(int), (int)sizeof(long),
        (int)sizeof(float), (int)sizeof(double));
    return 0;
}
