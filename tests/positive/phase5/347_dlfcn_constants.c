// TEST: dlfcn_constants
// DESCRIPTION: <dlfcn.h> must define RTLD_NOW/LAZY/LOCAL/GLOBAL and the dl*
// function prototypes. Repro from Lua loadlib.c.
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 2 1 4 8
// PHASE: 5

#include <stdio.h>
#include <dlfcn.h>

int main(void) {
    /* Verify the constants from the fallback header are present and distinct. */
    printf("%d %d %d %d\n", RTLD_NOW, RTLD_LAZY, RTLD_LOCAL, RTLD_GLOBAL);
    /* Take address of dlopen/dlsym to ensure the prototypes are visible. */
    void *p = (void *)&dlopen;
    void *q = (void *)&dlsym;
    (void)p; (void)q;
    return 0;
}
