// TEST: pread_pwrite_static_init
// DESCRIPTION: pread/pwrite/pwrite64 from unistd.h used as function pointers in static initializer
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* sqlite3.c aSyscall[] table uses pread (index 9) and pwrite/pwrite64 (indices 12/13)
   as function pointer initializers. jmcc's built-in unistd.h is missing these
   declarations, so the casts silently evaluate to 0. */

#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>

typedef void (*fn_ptr)(void);

struct syscall_entry {
    const char *name;
    fn_ptr pCurrent;
};

static struct syscall_entry tbl[] = {
    { "pread",   (fn_ptr)pread },
    { "pwrite",  (fn_ptr)pwrite },
    { "pwrite64",(fn_ptr)pwrite64 },
};

int main(void) {
    int fail = 0;
    for (int i = 0; i < 3; i++) {
        if (!tbl[i].pCurrent) {
            printf("FAIL: %s initializer is null\n", tbl[i].name);
            fail = 1;
        }
    }
    if (!fail) printf("ok\n");
    return fail;
}
