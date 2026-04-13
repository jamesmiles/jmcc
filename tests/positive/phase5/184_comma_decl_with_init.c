// TEST: comma_decl_with_init
// DESCRIPTION: Comma-separated global declarations with initializers must declare all variables
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Chocolate Doom's i_video.c declares:
     int fullscreen_width = 0, fullscreen_height = 0;
   jmcc only declares the first variable and ignores the rest.
   This is the last issue blocking Chocolate Doom compilation. */

int printf(const char *fmt, ...);

/* Two globals with initializers */
int width = 640, height = 480;

/* Three globals */
int r = 1, g = 2, b = 3;

/* Mixed initialized and uninitialized */
int count = 10, total;

/* With pointers */
char *name = "hello", *label = "world";

/* In a function (local) */
int sum(void) {
    int a = 3, b = 4, c = 5;
    return a + b + c;
}

int main(void) {
    /* Test 1: two globals with init */
    if (width != 640) return 1;
    if (height != 480) return 2;

    /* Test 2: three globals */
    if (r != 1) return 3;
    if (g != 2) return 4;
    if (b != 3) return 5;

    /* Test 3: mixed init */
    if (count != 10) return 6;

    /* Test 4: pointer globals */
    if (name[0] != 'h') return 7;
    if (label[0] != 'w') return 8;

    /* Test 5: local comma declarations */
    if (sum() != 12) return 9;

    /* Test 6: modify and check */
    width = 800;
    height = 600;
    if (width != 800) return 10;
    if (height != 600) return 11;

    printf("ok\n");
    return 0;
}
