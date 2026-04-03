// TEST: byte_member_unsigned_compare
// DESCRIPTION: Unsigned char (byte) struct member compared with 0xff must work correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's column drawing loop:
     while (column->topdelta != 0xff) { ... }
   where topdelta is unsigned char (byte). If loaded as signed char,
   the value 0xff becomes -1, which != 255, making the termination
   check fail. The loop then reads past the column data, corrupting
   memory or crashing.

   Also: column->topdelta * SCREENWIDTH must be unsigned to avoid
   negative offsets for values > 127. */

int printf(const char *fmt, ...);

typedef unsigned char byte;

typedef struct {
    byte topdelta;
    byte length;
} post_t;

int main(void) {
    post_t p;

    /* Test: 0xff must equal 0xff when compared as unsigned char */
    p.topdelta = 0xff;
    if (p.topdelta != 0xff) return 1;   /* fails if loaded as signed: -1 != 255 */

    /* Test: values > 127 must be treated as positive */
    p.topdelta = 200;
    int result = p.topdelta * 320;
    if (result != 64000) return 2;  /* fails if signed: -56 * 320 = -17920 */

    /* Test: comparison with literal works */
    p.topdelta = 254;
    if (p.topdelta == 0xff) return 3;  /* 254 != 255, should not match */

    p.topdelta = 0xff;
    if (p.topdelta == 0xff) {
        /* correct path */
    } else {
        return 4;  /* should not reach here */
    }

    printf("ok\n");
    return 0;
}
