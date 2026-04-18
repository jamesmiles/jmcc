// TEST: getpagesize
// DESCRIPTION: getpagesize from unistd.h used as function pointer in static initializer
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* sqlite3.c aSyscall[21] initializes pCurrent to getpagesize.
   jmcc's built-in unistd.h is missing getpagesize, so the cast
   silently evaluates to 0. */

#include <stdio.h>
#include <unistd.h>

typedef void (*fn_ptr)(void);

struct syscall_entry {
    const char *name;
    fn_ptr pCurrent;
};

static struct syscall_entry tbl[] = {
    { "getpagesize", (fn_ptr)getpagesize },
};

int main(void) {
    if (!tbl[0].pCurrent) {
        printf("FAIL: getpagesize initializer is null\n");
        return 1;
    }
    /* also verify it returns a sensible page size (power of 2, >= 4096) */
    int (*gps)(void) = (int (*)(void))tbl[0].pCurrent;
    int sz = gps();
    if (sz < 4096 || (sz & (sz - 1)) != 0) {
        printf("FAIL: bad page size %d\n", sz);
        return 1;
    }
    printf("ok\n");
    return 0;
}
