// TEST: sizeof_string_literal_arm64
// DESCRIPTION: sizeof("abc") must be 4 (char[N], not char*). Lua's ldump.c
// uses dumpLiteral(D, LUA_SIGNATURE) where the macro relies on
// sizeof("\x1bLua") == 5; arm64 was returning 8 (pointer size), corrupting
// the precompiled bytecode header so load() reported "version mismatch".
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 5 4 6 1 13
// PHASE: 5

#include <stdio.h>

#define MY_SIG "\x1bLua"

int main(void) {
    /* "\x1bLua" → 4 chars + NUL = 5 */
    printf("%zu %zu %zu %zu %zu\n",
           sizeof(MY_SIG),
           sizeof("abc"),
           sizeof("hello"),
           sizeof(""),
           sizeof("\x19\x93\r\n\x1a\nLuaver"));
    return 0;
}
