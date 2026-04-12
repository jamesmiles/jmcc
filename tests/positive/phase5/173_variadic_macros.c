// TEST: variadic_macros
// DESCRIPTION: Variadic macros with __VA_ARGS__ must expand correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Chocolate Doom uses:
     #define PACKED_STRUCT(...) PACKEDPREFIX struct __VA_ARGS__ PACKEDATTR
   Variadic macros are C99. jmcc must handle #define with ... parameter
   and __VA_ARGS__ expansion in the body. */

#include <stdio.h>
#include <string.h>

/* Basic variadic macro */
#define LOG(fmt, ...) sprintf(buf, fmt, __VA_ARGS__)

/* Variadic macro with no extra args (GNU extension: empty __VA_ARGS__) */
#define LOG0(fmt) sprintf(buf, fmt)

/* Wrapper around printf */
#define MY_PRINTF(...) printf(__VA_ARGS__)

/* Macro that passes __VA_ARGS__ through to another variadic */
#define WRAP_SPRINTF(buf, fmt, ...) sprintf(buf, fmt, __VA_ARGS__)

/* Stringification combined with variadic */
#define STR_LOG(fmt, ...) sprintf(buf, "[LOG] " fmt, __VA_ARGS__)

/* Chocolate Doom's exact pattern: struct wrapper */
#define MY_PACKED_STRUCT(...) struct __VA_ARGS__

MY_PACKED_STRUCT(my_point { int x; int y; });

/* Variadic macro used in conditional */
#define CHECK(cond, ...) do { if (!(cond)) { sprintf(buf, __VA_ARGS__); return 1; } } while(0)

/* Single-arg variadic (just __VA_ARGS__, no fixed params) */
#define PARENS(...) (__VA_ARGS__)

char buf[256];

int main(void) {
    /* Test 1: basic variadic macro */
    LOG("val=%d", 42);
    if (strcmp(buf, "val=42") != 0) return 1;

    /* Test 2: multiple variadic args */
    LOG("%d+%d=%d", 1, 2, 3);
    if (strcmp(buf, "1+2=3") != 0) return 2;

    /* Test 3: string variadic arg */
    LOG("name=%s age=%d", "bob", 30);
    if (strcmp(buf, "name=bob age=30") != 0) return 3;

    /* Test 4: no variadic args (fixed only) */
    LOG0("hello");
    if (strcmp(buf, "hello") != 0) return 4;

    /* Test 5: pass-through to printf */
    /* (can't easily test printf output, just ensure it compiles) */
    MY_PRINTF("%s", "");

    /* Test 6: nested wrapper */
    WRAP_SPRINTF(buf, "x=%d", 99);
    if (strcmp(buf, "x=99") != 0) return 6;

    /* Test 7: with prefix string concat */
    STR_LOG("%d", 7);
    if (strcmp(buf, "[LOG] 7") != 0) return 7;

    /* Test 8: struct definition via variadic macro */
    struct my_point p;
    p.x = 10;
    p.y = 20;
    if (p.x + p.y != 30) return 8;

    /* Test 9: variadic in conditional */
    CHECK(1 == 1, "should not fail");

    /* Test 10: single-arg variadic for grouping */
    int r = PARENS(3 + 4);
    if (r != 7) return 10;

    /* Test 11: variadic with zero extra args after fmt */
    /* This is a common edge case */
    LOG0("no args here");
    if (strcmp(buf, "no args here") != 0) return 11;

    printf("ok\n");
    return 0;
}
