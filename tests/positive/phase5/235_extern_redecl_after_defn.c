// TEST: extern_redecl_after_defn
// DESCRIPTION: a second extern declaration after a definition must not suppress the definition
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* In C, a translation unit may have an extern declaration for a symbol
   both before and after its definition (e.g., a header included twice,
   or os_common.h appearing in two different .c files of an amalgamation).
   The second extern re-declaration must not cause jmcc to suppress the
   .globl and .data section entry for the symbol.

   Failing pattern (from SQLite amalgamation sqlite3.c):

     extern int sqlite3_io_error_hit;     // os_common.h, first inclusion
     int sqlite3_io_error_hit = 0;        // definition in os.c section
     extern int sqlite3_io_error_hit;     // os_common.h, second inclusion

   jmcc emits no .globl and no .long for sqlite3_io_error_hit or
   sqlite3_io_error_pending, so the linker reports undefined references
   when test2.c and test_journal.c try to use them in testfixture. */

extern int g_hit;
extern int g_pending;

int g_hit = 11;
int g_hardhit = 22;    /* no second extern below — control case */
int g_pending = 33;

/* second extern declarations (simulates header re-inclusion) */
extern int g_pending;
extern int g_hit;

int read_hit(void)     { return g_hit; }
int read_pending(void) { return g_pending; }
int read_hardhit(void) { return g_hardhit; }

#include <stdio.h>
int main(void) {
    if (read_hit()     != 11) { printf("FAIL hit: %d\n",     read_hit());     return 1; }
    if (read_hardhit() != 22) { printf("FAIL hardhit: %d\n", read_hardhit()); return 2; }
    if (read_pending() != 33) { printf("FAIL pending: %d\n", read_pending()); return 3; }
    printf("ok\n");
    return 0;
}
