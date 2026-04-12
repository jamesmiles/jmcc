// TEST: array_sizeof_then_pass
// DESCRIPTION: Array used in sizeof must still decay to pointer when passed to function
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's am_map.c has:
     mline_t player_arrow[] = { ... };
     #define NUMPLYRLINES (sizeof(player_arrow)/sizeof(mline_t))
     AM_drawLineCharacter(player_arrow, NUMPLYRLINES, ...);
   jmcc loads the array DATA instead of passing its ADDRESS when
   sizeof(array) was used in the same expression or scope.
   This crashes the automap (Tab key) because the function receives
   garbage data instead of a valid pointer. */

int printf(const char *fmt, ...);

typedef struct { int x; int y; } point_t;
typedef struct { point_t a; point_t b; } line_t;

line_t arrows[] = {
    { {-1, 0}, {1, 0} },
    { {1, 0}, {0, 1} },
    { {0, 1}, {-1, 0} }
};

#define NUM_ARROWS (sizeof(arrows)/sizeof(line_t))

/* Function that receives array as pointer */
int sum_lines(line_t *lines, int count) {
    int total = 0;
    for (int i = 0; i < count; i++) {
        total += lines[i].a.x + lines[i].a.y + lines[i].b.x + lines[i].b.y;
    }
    return total;
}

/* 7-arg function like AM_drawLineCharacter */
int draw_lines(line_t *lines, int count, int scale, int angle, int color, int x, int y) {
    int total = 0;
    for (int i = 0; i < count; i++) {
        total += lines[i].a.x * scale + x;
        total += lines[i].b.y * scale + y;
    }
    return total + color + angle;
}

int main(void) {
    /* Test 1: sizeof used, then array passed as pointer */
    int n = NUM_ARROWS;
    if (n != 3) return 1;
    int r = sum_lines(arrows, NUM_ARROWS);
    /* (-1+0+1+0) + (1+0+0+1) + (0+1+-1+0) = 0 + 2 + 0 = 2 */
    if (r != 2) return 2;

    /* Test 2: sizeof in same call expression */
    r = sum_lines(arrows, sizeof(arrows)/sizeof(line_t));
    if (r != 2) return 3;

    /* Test 3: 7-arg function (Doom's exact pattern) */
    r = draw_lines(arrows, NUM_ARROWS, 1, 0, 0, 0, 0);
    /* (-1*1+0) + (0*1+0) + (1*1+0) + (1*1+0) + (0*1+0) + (0*1+0) = -1+0+1+1+0+0 = 1 */
    if (r != 1) return 4;

    /* Test 4: verify pointer is valid (not array data) */
    line_t *p = arrows;
    if (p != arrows) return 5;
    if (p[0].a.x != -1) return 6;

    printf("ok\n");
    return 0;
}
