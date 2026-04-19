// TEST: macro_3level_string_escape
// DESCRIPTION: 3-level macro expansion with string escapes and variadic args
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK  
// ENVIRONMENT: hosted
#include <stdio.h>

#define LOG_LVL_ERR 3
#define LOG_BASE(lvl, ...) printf(__VA_ARGS__)
#define LOG_ERR(...) LOG_BASE(LOG_LVL_ERR, __VA_ARGS__)
#define PRINT_NODE_ERR(n, err) \
    LOG_ERR("Node %s replied with error:\n%s\n", \
            (n), (err));

int main(void) {
    PRINT_NODE_ERR("mynode", "someerror");
    printf("OK\n");
    return 0;
}
