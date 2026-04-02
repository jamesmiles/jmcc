// TEST: multiline_call_inline_comment
// DESCRIPTION: Multi-line function call with // comments after arguments
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: sum=15
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

int add5(int a, int b, int c, int d, int e) {
    return a + b + c + d + e;
}

int main(void) {
    /* Doom's i_video.c calls XCreateWindow with inline comments:
         XCreateWindow( display,
                        root,
                        x, y,
                        width, height,
                        0, // borderwidth
                        8, // depth
                        InputOutput,
                        visual,
                        mask,
                        &attribs );
       The // comments after args must not break multi-line joining. */
    int result = add5(
        1,     // first
        2,     // second
        3,     // third
        4,     // fourth
        5);    // fifth
    printf("sum=%d\n", result);
    return 0;
}
