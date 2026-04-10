// TEST: int_to_ptr_cast_store
// DESCRIPTION: Storing (void*)small_int to a pointer field must write full 8 bytes
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* z_zone.c does: base->user = (void *)2;
   This stores a small integer (2) cast to a pointer. The store must
   write all 8 bytes (clearing upper 32 bits). If it uses movl (4 bytes),
   the upper 4 bytes retain whatever was there before, creating a
   corrupted pointer value like 0x7fff00000002 that passes some
   checks but fails others. */

int printf(const char *fmt, ...);

struct block {
    int size;
    void **user;
};

int main(void) {
    struct block b;

    /* First set user to a real pointer (high bits set) */
    char dummy;
    b.user = (void **)&dummy;  /* e.g. 0x7fffffffe123 */

    /* Now overwrite with (void *)2 — must clear all 8 bytes */
    b.user = (void *)2;

    /* Check the full 8-byte value */
    long val = (long)b.user;
    if (val != 2) return 1;  /* fails if upper bytes retained */

    /* Also test (void *)0 (NULL) */
    b.user = (void **)&dummy;
    b.user = (void *)0;
    val = (long)b.user;
    if (val != 0) return 2;

    /* Test storing to a void* local */
    void *p = (void *)&dummy;
    p = (void *)0x100;
    val = (long)p;
    if (val != 0x100) return 3;

    printf("ok\n");
    return 0;
}
