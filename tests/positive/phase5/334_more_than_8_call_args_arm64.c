/* Regression: function calls with more than 8 arguments must work on
 * arm64-apple-darwin.
 *
 * The arm64 ABI passes the first 8 integer/pointer arguments in registers
 * x0-x7; additional arguments are passed on the stack. jmcc must emit
 * correct stack-spill code for the 9th and subsequent arguments.
 *
 * Mirrors SDL_CreateRGBSurfaceFrom() in Chocolate Doom's i_video.c:
 *
 *   surface = SDL_CreateRGBSurfaceFrom(
 *       (void *) icon_data, icon_w, icon_h, 32, icon_w * 4,
 *       0xffu << 24, 0xffu << 16, 0xffu << 8, 0xffu << 0);  // 9 args
 */

/* 9-argument function */
int sum9(int a, int b, int c, int d, int e,
         int f, int g, int h, int i) {
    return a + b + c + d + e + f + g + h + i;
}

/* 10-argument function */
int sum10(int a, int b, int c, int d, int e,
          int f, int g, int h, int i, int j) {
    return a + b + c + d + e + f + g + h + i + j;
}

int main(void) {
    int r9  = sum9 (1, 2, 3, 4, 5, 6, 7, 8, 9);        /* 45 */
    int r10 = sum10(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);    /* 55 */
    return (r9 == 45 && r10 == 55) ? 0 : 1;
}
