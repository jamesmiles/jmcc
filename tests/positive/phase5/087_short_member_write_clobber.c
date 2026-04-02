// TEST: short_member_write_clobber
// DESCRIPTION: Writing to a short struct member must use 2-byte store, not 4-byte
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's doomcom_t has many adjacent short members (ticdup, numnodes, etc.).
   Writing to one short member with movl (4 bytes) instead of movw (2 bytes)
   clobbers the adjacent member. In Doom, writing numnodes=1 zeroes ticdup,
   then BACKUPTICS/(2*ticdup) triggers a division-by-zero (SIGFPE) in
   D_CheckNetGame. */

int printf(const char *fmt, ...);
void *malloc(unsigned long);
void *memset(void *, int, unsigned long);

typedef struct { int id; short x; short y; } S;

int main(void) {
    S *p = malloc(sizeof(S));
    memset(p, 0, sizeof(*p));
    p->y = 42;
    p->x = 10;
    if (p->y != 42) return 1;
    if (p->x != 10) return 2;
    printf("ok\n");
    return 0;
}
