/* struct array initializer with macro arithmetic expression as size was emitting
   empty data (just the label) because the array-of-structs codepath only handled
   IntLiteral sizes, not BinaryOp constant expressions from macro expansion */
#include <stdio.h>

typedef unsigned short ush;
typedef struct {
    union { ush freq; ush code; } fc;
    union { ush dad;  ush len;  } dl;
} ct_data;

static const ct_data first[3] = {{{10},{1}}, {{20},{2}}, {{30},{3}}};

#define A 2
#define B 3
static const ct_data second[A+B] = {
    {{100},{8}}, {{140},{8}}, {{76},{8}}, {{25},{8}}, {{44},{8}}
};

#define LITERALS 4
#define EXTRA 1
#define TOTAL (LITERALS + EXTRA)
static const ct_data third[TOTAL] = {
    {{1},{7}}, {{2},{7}}, {{3},{7}}, {{4},{7}}, {{5},{7}}
};

int main(void) {
    /* Verify first array is unaffected */
    if (first[2].fc.code != 30 || first[2].dl.len != 3) return 1;
    /* Verify second array (size = A+B = 5) has correct data */
    if (second[0].fc.code != 100 || second[0].dl.len != 8) return 2;
    if (second[3].fc.code != 25  || second[3].dl.len != 8) return 3;
    if (second[4].fc.code != 44  || second[4].dl.len != 8) return 4;
    /* Verify third array (size = LITERALS+EXTRA = 5) has correct data */
    if (third[0].fc.code != 1 || third[0].dl.len != 7) return 5;
    if (third[4].fc.code != 5 || third[4].dl.len != 7) return 6;
    printf("OK\n");
    return 0;
}
