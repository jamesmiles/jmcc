// TEST: pread64_static_init
// DESCRIPTION: pread64 from unistd.h used as function pointer in static struct initializer
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* sqlite3.c lines 38441-38442:
     #if defined(USE_PREAD64)
       { "pread64", (sqlite3_syscall_ptr)pread64, 0 },
   Bug: jmcc's built-in unistd.h lacks pread64, so the cast
   (sqlite3_syscall_ptr)pread64 silently evaluates to 0 in the static
   initializer. */

#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>

typedef void (*fn_ptr)(void);

struct syscall_entry {
    const char *name;
    fn_ptr pCurrent;
};

static struct syscall_entry tbl[] = {
    { "pread64", (fn_ptr)pread64 },
};

int main(void) {
    if (!tbl[0].pCurrent) {
        printf("FAIL: pread64 initializer is null\n");
        return 1;
    }
    printf("ok\n");
    return 0;
}
