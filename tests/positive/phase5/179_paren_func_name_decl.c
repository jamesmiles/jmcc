// TEST: paren_func_name_decl
// DESCRIPTION: Parenthesized function name in declaration must parse
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* libpng headers (included by Chocolate Doom's v_video.c) use:
     extern png_uint_32 (png_access_version_number)(void);
   The function name is wrapped in parentheses. This is valid C —
   the parens are redundant but legal in declarators. jmcc must
   accept this syntax. */

int printf(const char *fmt, ...);

/* Parenthesized function name in declaration */
extern int (add_nums)(int a, int b);

/* Definition with parens */
int (add_nums)(int a, int b) {
    return a + b;
}

/* Pointer to parenthesized-name function */
int (*fptr)(int, int) = add_nums;

int main(void) {
    if (add_nums(3, 4) != 7) return 1;
    if (fptr(10, 20) != 30) return 2;

    printf("ok\n");
    return 0;
}
