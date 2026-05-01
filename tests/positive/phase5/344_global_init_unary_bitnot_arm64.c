// TEST: global_init_unary_bitnot_arm64
// DESCRIPTION: Global initializers using unary ~/+/! must constant-fold on arm64.
// Repro derived from Lua 5.4 lcode.c:
//   static const Instruction invalidinstruction = ~(Instruction)0;
// Prior to fix, arm64 _global_const_int folded only unary '-', so ~/!/+ on a
// global initializer raised "backend does not yet support this global initializer value".
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: 4294967295 1 0 0 7
// PHASE: 5

#include <stdio.h>

typedef unsigned int Instruction;

static const Instruction invalidinstruction = ~(Instruction)0;
static const int not_zero = !0;
static const int not_seven = !7;
static const int plus_zero = +0;
static const int plus_seven = +7;

int main(void) {
    printf("%u %d %d %d %d\n",
           invalidinstruction, not_zero, not_seven, plus_zero, plus_seven);
    return 0;
}
