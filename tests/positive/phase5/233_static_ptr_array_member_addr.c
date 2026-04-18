// TEST: static_ptr_array_member_addr
// DESCRIPTION: static local pointer array initialised with &global_struct.member[N] addresses
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* d9a13c2 fixed static local pointer arrays whose elements are plain
   global variable addresses (e.g. `static int *ap[] = {r1, r2}`).
   But when the initialiser elements are address-of-member expressions
   like `&g.a[1]` or `&g.b[2]`, the global-init resolver does not
   recognise them as relocatable addresses and emits `.quad 0` instead
   of `.quad g+offset`, leaving all entries as NULL.

   Reduced from SQLite shell.c isKnownWritable():

       static PerStreamTags *apst[] = {
           &consoleInfo.pstDesignated[1],
           &consoleInfo.pstDesignated[2],
           &consoleInfo.pstSetup[1],
           &consoleInfo.pstSetup[2], 0
       };
       do { if( apst[ix]->pf == pf ) break; } while( apst[++ix] != 0 );

   With NULL entries, apst[0]->pf crashes immediately (SEGV at address 8,
   which is offsetof(PerStreamTags, pf)). */

#include <stdio.h>

typedef struct { short reach; int *p; } Tag;
typedef struct { Tag a[3]; Tag b[3]; } Info;

static Info g;

static Tag *lookup(int i) {
    static Tag *arr[] = {
        &g.a[1], &g.a[2],
        &g.b[1], &g.b[2], 0
    };
    return arr[i];
}

int main(void) {
    g.a[1].reach = 11;
    g.a[2].reach = 12;
    g.b[1].reach = 21;
    g.b[2].reach = 22;

    if (lookup(0) != &g.a[1]) { printf("FAIL ptr[0] wrong\n"); return 1; }
    if (lookup(0)->reach != 11) { printf("FAIL reach[0]=%d\n", lookup(0)->reach); return 2; }
    if (lookup(1)->reach != 12) { printf("FAIL reach[1]=%d\n", lookup(1)->reach); return 3; }
    if (lookup(2)->reach != 21) { printf("FAIL reach[2]=%d\n", lookup(2)->reach); return 4; }
    if (lookup(3)->reach != 22) { printf("FAIL reach[3]=%d\n", lookup(3)->reach); return 5; }
    if (lookup(4) != 0)         { printf("FAIL sentinel not null\n"); return 6; }
    printf("ok\n");
    return 0;
}
