// TEST: system_define_substitute
// DESCRIPTION: Doom's M_ClearBox uses MININT/MAXINT from <values.h>; tests the bbox pattern
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: -2147483648
// STDOUT: 2147483647
// STDOUT: reset
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

/* Doom's m_bbox.h pulls MININT/MAXINT from <values.h>.
   JMCC doesn't support all system headers, so Doom uses local fallbacks. */
#define MININT ((int)0x80000000)
#define MAXINT ((int)0x7FFFFFFF)

#define BOXTOP    0
#define BOXBOTTOM 1
#define BOXLEFT   2
#define BOXRIGHT  3

void M_ClearBox(int *box) {
    box[BOXTOP] = box[BOXRIGHT] = MININT;
    box[BOXBOTTOM] = box[BOXLEFT] = MAXINT;
}

int main(void) {
    int box[4];
    M_ClearBox(box);
    printf("%d\n", box[BOXTOP]);
    printf("%d\n", box[BOXBOTTOM]);

    if (box[BOXTOP] < 0 && box[BOXBOTTOM] > 0)
        printf("reset\n");
    return 0;
}
