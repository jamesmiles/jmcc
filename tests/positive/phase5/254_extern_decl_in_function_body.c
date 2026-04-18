// TEST: extern_decl_in_function_body
// DESCRIPTION: extern decl inside function body must resolve to global, not allocate a local variable
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>

int g_counter = 0;

/* extern decl inside function body must resolve to global, not allocate a local */
void increment_via_extern(void) {
    extern int g_counter;
    g_counter++;
}

/* also test inside a conditional block */
void conditional_extern(int flag) {
    if (flag) {
        extern int g_counter;
        g_counter += 10;
    }
}

int main(void) {
    increment_via_extern();
    if (g_counter != 1) {
        printf("FAIL: after increment_via_extern g_counter=%d expected 1\n", g_counter);
        return 1;
    }
    conditional_extern(1);
    if (g_counter != 11) {
        printf("FAIL: after conditional_extern g_counter=%d expected 11\n", g_counter);
        return 1;
    }
    printf("ok\n");
    return 0;
}
