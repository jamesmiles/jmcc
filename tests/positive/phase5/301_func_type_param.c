// TEST: func_type_param
// DESCRIPTION: function type used directly as parameter (not pointer, not typedef) must decay to pointer: void fn(void(cb)(int))
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

static int called = 0;

/* function type as parameter — decays to function pointer */
void apply(int x, void(callback)(int)) {
    callback(x);
}

static void my_cb(int v) {
    called = v;
}

int main(void) {
    apply(42, my_cb);
    if (called != 42) return 1;
    printf("OK\n");
    return 0;
}
