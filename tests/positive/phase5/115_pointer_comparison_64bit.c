// TEST: pointer_comparison_64bit
// DESCRIPTION: Pointer equality/inequality comparison must use 64-bit cmpq not 32-bit cmpl
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* z_zone.c's Z_Malloc has: if (rover == start) ...
   Two pointers compared with cmpl instead of cmpq. If they
   share the same lower 32 bits but differ in upper bits,
   cmpl says they're equal when they're not.

   This affects all pointer ==, !=, <, >, <=, >= comparisons. */

int printf(const char *fmt, ...);

int main(void) {
    /* Two pointers that differ only in upper 32 bits */
    char *a = (char *)0x100000000L;
    char *b = (char *)0x200000000L;

    /* These are different pointers */
    if (a == b) return 1;   /* FAILS with cmpl: both have 0x00000000 in low 32 bits */
    if (!(a != b)) return 2;

    /* Same lower 32 bits, different upper */
    char *c = (char *)0x1000000FF;
    char *d = (char *)0x2000000FF;
    if (c == d) return 3;

    /* NULL comparison (should still work) */
    char *n = (char *)0;
    if (n != (char *)0) return 4;

    /* Pointer relational comparison */
    if (!(b > a)) return 5;  /* 0x200000000 > 0x100000000 */
    if (a >= b) return 6;

    /* The Z_Malloc pattern: comparing struct pointers */
    struct block { int x; struct block *next; };
    struct block *p1 = (struct block *)0x100000000L;
    struct block *p2 = (struct block *)0x200000000L;
    if (p1 == p2) return 7;

    printf("ok\n");
    return 0;
}
