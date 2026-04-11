// TEST: incr_short_member_clobber
// DESCRIPTION: Increment/decrement on short struct member must not clobber adjacent bytes
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* The unary ++/-- code path (gen_unary) uses movl for all non-pointer
   types, writing 4 bytes for a short member and clobbering the next
   field. This is a variant of the compound assignment clobber bug. */

int printf(const char *fmt, ...);

struct header {
    short tag;
    short id;
    int size;
};

int main(void) {
    struct header h;
    h.tag = 100;
    h.id = 0x1D4A;  /* Doom ZONEID constant */
    h.size = 65536;

    /* Post-increment on short member */
    h.tag++;

    if (h.tag != 101) return 1;
    if (h.id != 0x1D4A) return 2;  /* fails if clobbered */
    if (h.size != 65536) return 3;

    /* Pre-decrement */
    --h.tag;

    if (h.tag != 100) return 4;
    if (h.id != 0x1D4A) return 5;

    /* Post-decrement */
    h.id--;

    if (h.tag != 100) return 6;  /* h.id is after h.tag, so no clobber backwards */
    if (h.id != 0x1D49) return 7;
    if (h.size != 65536) return 8;

    printf("ok\n");
    return 0;
}
