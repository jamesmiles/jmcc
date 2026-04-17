// TEST: bitfield_writes
// DESCRIPTION: Bitfield writes must update the named field without affecting siblings
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SQLite's Index struct has many adjacent 1-bit bitfields:
     unsigned hasStat1:1;
     unsigned bLowQual:1;
     unsigned bNoQuery:1;
     ...
   jmcc fails to write bitfields correctly. After several assignments,
   reads return wrong values (e.g., a 1-bit field reading as 3).
   The query planner reads bNoQuery as nonzero when it should be 0,
   skipping the only available query plan. CREATE TABLE then fails
   with "no query solution" because the schema query can't be planned. */

int printf(const char *fmt, ...);

typedef struct {
    unsigned a:1;
    unsigned b:1;
    unsigned c:1;
    unsigned d:1;
    unsigned e:1;
    unsigned f:1;
    unsigned g:1;
    unsigned h:1;
} Flags;

int main(void) {
    Flags x = {0};

    /* Single writes */
    x.a = 1;
    if (x.a != 1) return 1;
    if (x.b != 0) return 2;

    x.c = 1;
    if (x.a != 1) return 3;  /* a must still be 1 */
    if (x.c != 1) return 4;
    if (x.b != 0) return 5;
    if (x.d != 0) return 6;

    /* Toggle */
    x.a = 0;
    if (x.a != 0) return 7;
    if (x.c != 1) return 8;  /* c must still be 1 */

    /* All eight fields, alternating */
    Flags y = {0};
    y.a = 1; y.b = 0; y.c = 1; y.d = 0;
    y.e = 1; y.f = 0; y.g = 1; y.h = 0;
    if (y.a != 1 || y.b != 0 || y.c != 1 || y.d != 0) return 10;
    if (y.e != 1 || y.f != 0 || y.g != 1 || y.h != 0) return 11;

    /* Bitfield sizes — values must be 0 or 1, never larger */
    if (y.a > 1) return 12;
    if (y.c > 1) return 13;

    printf("ok\n");
    return 0;
}
