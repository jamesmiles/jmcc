// TEST: struct_copy_variants
// DESCRIPTION: All struct copy operations must copy the full struct, not just first field
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Test all variants of struct copy that might only copy the first field. */

int printf(const char *fmt, ...);

typedef struct { int a; int b; int c; } triple_t;

/* Return struct by value */
triple_t make_triple(int x, int y, int z) {
    triple_t t;
    t.a = x;
    t.b = y;
    t.c = z;
    return t;
}

/* Accept struct by value */
int sum_triple(triple_t t) {
    return t.a + t.b + t.c;
}

triple_t global_t;

int main(void) {
    triple_t src;
    src.a = 10;
    src.b = 20;
    src.c = 30;

    /* 1. Local struct = local struct */
    triple_t dst = src;
    if (dst.b != 20) return 1;
    if (dst.c != 30) return 2;

    /* 2. Global = local */
    global_t = src;
    if (global_t.b != 20) return 3;
    if (global_t.c != 30) return 4;

    /* 3. Local = function return */
    triple_t ret = make_triple(100, 200, 300);
    if (ret.a != 100) return 5;
    if (ret.b != 200) return 6;
    if (ret.c != 300) return 7;

    /* 4. Pass struct by value */
    int total = sum_triple(src);
    if (total != 60) return 8;

    /* 5. Array of structs copy */
    triple_t arr[3];
    arr[0] = src;
    if (arr[0].b != 20) return 9;
    if (arr[0].c != 30) return 10;

    /* 6. Through pointer dereference */
    triple_t *p = &src;
    triple_t copy = *p;
    if (copy.b != 20) return 11;
    if (copy.c != 30) return 12;

    /* 7. Larger struct (> 16 bytes) */
    typedef struct { int w[8]; } big_t;
    big_t big_src;
    int i;
    for (i = 0; i < 8; i++) big_src.w[i] = i * 10;
    big_t big_dst = big_src;
    if (big_dst.w[3] != 30) return 13;
    if (big_dst.w[7] != 70) return 14;

    printf("ok\n");
    return 0;
}
