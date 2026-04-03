// TEST: compound_assign_char_clobber
// DESCRIPTION: Compound assignment on char struct member must not clobber adjacent bytes on overflow
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Same class of bug as 089 but for char members. Compound assignment
   emits movl (4 bytes) instead of movb (1 byte). The 4-byte
   read-modify-write usually preserves adjacent data, but when the
   char operation overflows, the carry corrupts the next byte(s). */

int printf(const char *fmt, ...);

struct record {
    char type;
    char flags;
    char priority;
    char padding;
    int value;
};

int main(void) {
    struct record r;

    /* Test 1: char overflow carries into adjacent byte */
    r.type = -1;      /* 0xFF */
    r.flags = 0;
    r.priority = 0;
    r.padding = 0;
    r.value = 12345;

    r.type += 1;       /* should become 0, carry must NOT affect r.flags */

    if (r.type != 0) return 1;
    if (r.flags != 0) return 2;   /* FAILS with movl: carry makes r.flags = 1 */

    /* Test 2: underflow borrows from adjacent byte */
    r.type = 0;
    r.flags = 1;
    r.type -= 1;       /* should become -1 (0xFF), must NOT borrow from r.flags */

    if (r.type != -1) return 3;
    if (r.flags != 1) return 4;   /* FAILS with movl: borrow makes r.flags = 0 */

    /* Test 3: overflow propagates further */
    r.type = -1;       /* 0xFF */
    r.flags = -1;      /* 0xFF */
    r.priority = 0;
    r.padding = 0;

    r.type += 1;       /* 4-byte: 0x0000FFFF + 1 = 0x00010000, corrupts priority */

    if (r.type != 0) return 5;
    if (r.flags != -1) return 6;  /* flags carries: 0xFF+carry=0x00, FAILS */

    printf("ok\n");
    return 0;
}
