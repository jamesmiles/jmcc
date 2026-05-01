// TEST: global_init_cast_string_arm64
// DESCRIPTION: Global pointer initializer of (cast)"literal" must emit a
// pointer to the string. Repro from SQLite trim() implementation:
//   static unsigned char * const azOne[] = { (u8*)" " };
// arm64 was rejecting CastExpr around StringLiteral in global init.
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: hello
// EXPECTED_STDOUT: x
// PHASE: 5

#include <stdio.h>

typedef unsigned char u8;
static const char * const greetings[] = { (const char*)"hello" };
static u8 * const azOne[] = { (u8*)"x" };

int main(void) {
    printf("%s\n", greetings[0]);
    printf("%s\n", (const char *)azOne[0]);
    return 0;
}
