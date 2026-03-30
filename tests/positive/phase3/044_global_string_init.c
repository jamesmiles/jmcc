// TEST: global_string_init
// DESCRIPTION: Global char array initialized from string literal
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: Hello
// ENVIRONMENT: hosted
// PHASE: 3

int printf(const char *fmt, ...);

char greeting[] = "Hello";

int main(void) {
    printf("%s\n", greeting);
    return 0;
}
