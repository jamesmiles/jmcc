// TEST: macro_multiline_args
// DESCRIPTION: Function-like macro call with arguments spanning multiple lines
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 30
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

/* Doom calls RootWindow(X_display,
                         X_screen) with args split across lines.
   The preprocessor must handle this. */
#define ADD(a, b) ((a) + (b))

int main(void) {
    int result = ADD(10,
                     20);
    printf("%d\n", result);
    return 0;
}
