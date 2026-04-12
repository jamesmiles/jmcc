// TEST: typedef_attribute
// DESCRIPTION: typedef with trailing __attribute__ must parse correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* System headers (glibc sys/types.h) use:
     typedef int register_t __attribute__((__mode__(__word__)));
   jmcc fails to parse __attribute__ after the typedef name.
   This prevents compiling any code that includes SDL2 headers,
   because SDL2/SDL_stdinc.h includes sys/types.h. */

int printf(const char *fmt, ...);

/* __attribute__ after typedef name */
typedef int myint_t __attribute__((aligned(4)));

/* __attribute__ after struct typedef */
typedef struct { int x; int y; } point_t __attribute__((aligned(8)));

/* Multiple attributes */
typedef unsigned short word_t __attribute__((aligned(2)));

int main(void) {
    myint_t a = 42;
    point_t p;
    word_t w = 100;

    p.x = 10;
    p.y = 20;

    if (a != 42) return 1;
    if (p.x + p.y != 30) return 2;
    if (w != 100) return 3;

    printf("ok\n");
    return 0;
}
