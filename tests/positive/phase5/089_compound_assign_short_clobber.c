// TEST: compound_assign_short_clobber
// DESCRIPTION: Compound assignment (+=) on short struct member must not clobber adjacent bytes
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Bug 087 fixed movl→movw for regular assignment (=) to short members.
   But compound assignments (+=, -=, |=, etc.) use a separate code path
   that still emits movl, writing 4 bytes instead of 2.

   In most cases the 4-byte read-modify-write preserves adjacent data,
   but when the short operation overflows (wraps past 0x7FFF or below 0),
   the carry propagates into the adjacent field, corrupting it.

   Doom's zone allocator memblock_t has adjacent short-sized fields.
   Any compound op that causes a short field to overflow would corrupt
   the neighboring zone block header field. */

int printf(const char *fmt, ...);

struct packed {
    short a;
    short b;
    int c;
};

int main(void) {
    struct packed s;

    /* Test 1: simple compound assign (no overflow - should work even with bug) */
    s.a = 10;
    s.b = 100;
    s.c = 42;
    s.a += 5;

    if (s.a != 15) return 1;
    if (s.b != 100) return 2;
    if (s.c != 42) return 3;

    /* Test 2: compound assign with overflow - short wraps, should NOT affect s.b */
    s.a = 32767;  /* 0x7FFF - max positive short */
    s.b = 500;
    s.a += 1;     /* should wrap to -32768, but NOT change s.b */

    /* With movl bug: 4-byte read = 0x01F47FFF, add 1 = 0x01F48000
       s.a becomes -32768 (correct), s.b becomes 0x01F4=500 (happens to be ok)
       But with different values the carry DOES corrupt. */

    /* Test 3: compound assign where carry definitely corrupts */
    s.a = -1;     /* 0xFFFF */
    s.b = 0;
    s.a += 1;     /* should become 0, but the carry from 0xFFFF+1=0x10000
                     propagates into s.b with movl, making s.b = 1 */

    if (s.a != 0) return 4;
    if (s.b != 0) return 5;   /* FAILS if movl clobbers: s.b becomes 1 */

    /* Test 4: subtraction underflow corrupts adjacent field */
    s.a = 0;
    s.b = 1;
    s.a -= 1;     /* should become -1 (0xFFFF), but 4-byte sub borrows from s.b */

    if (s.a != -1) return 6;
    if (s.b != 1) return 7;   /* FAILS if movl clobbers: s.b becomes 0 */

    printf("ok\n");
    return 0;
}
