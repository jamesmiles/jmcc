// TEST: readlink_fchown_static_init
// DESCRIPTION: readlink and fchown from unistd.h used as function pointers in static initializer
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* sqlite3.c aSyscall[] uses readlink (index 24) and fchown (index 15) as
   function pointer initializers. jmcc's built-in unistd.h is missing both,
   so the casts silently evaluate to 0. */

#include <stdio.h>
#include <unistd.h>

typedef void (*fn_ptr)(void);

struct syscall_entry {
    const char *name;
    fn_ptr pCurrent;
};

static struct syscall_entry tbl[] = {
    { "readlink", (fn_ptr)readlink },
    { "fchown",   (fn_ptr)fchown },
};

int main(void) {
    int fail = 0;
    for (int i = 0; i < 2; i++) {
        if (!tbl[i].pCurrent) {
            printf("FAIL: %s initializer is null\n", tbl[i].name);
            fail = 1;
        }
    }
    if (!fail) printf("ok\n");
    return fail;
}
