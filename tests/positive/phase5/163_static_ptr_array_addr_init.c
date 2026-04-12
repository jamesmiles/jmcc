// TEST: static_ptr_array_addr_init
// DESCRIPTION: Static pointer array initialized with addresses of other static data must not be zero
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's wi_stuff.c has:
     static anim_t epsd0animinfo[] = { ... };
     static anim_t *anims[3] = { epsd0animinfo, epsd1animinfo, epsd2animinfo };
   jmcc emits anims as all zeros instead of the actual addresses.
   This causes a NULL dereference crash on the E1M1 intermission screen. */

int printf(const char *fmt, ...);

typedef struct {
    int type;
    int count;
    int data[3];
} info_t;

static info_t group0[] = {
    { 0, 3, {10, 20, 30} },
    { 1, 2, {40, 50, 0} }
};

static info_t group1[] = {
    { 2, 1, {60, 0, 0} }
};

static info_t group2[] = {
    { 3, 3, {70, 80, 90} },
    { 4, 2, {100, 110, 0} },
    { 5, 1, {120, 0, 0} }
};

/* Pointer array initialized with addresses of static arrays */
static info_t *groups[] = {
    group0,
    group1,
    group2
};

static int counts[] = {2, 1, 3};

/* Same pattern with simple types */
static int arr_a[] = {1, 2, 3};
static int arr_b[] = {4, 5};
static int *ptrs[] = { arr_a, arr_b };

int main(void) {
    /* Test 1: pointer array elements are non-NULL */
    if (groups[0] == 0) return 1;
    if (groups[1] == 0) return 2;
    if (groups[2] == 0) return 3;

    /* Test 2: access through pointer array */
    if (groups[0][0].type != 0) return 4;
    if (groups[0][0].data[0] != 10) return 5;
    if (groups[0][1].count != 2) return 6;

    /* Test 3: different groups */
    if (groups[1][0].data[0] != 60) return 7;
    if (groups[2][2].data[0] != 120) return 8;

    /* Test 4: Doom's exact pattern - iterate with count */
    int total = 0;
    for (int g = 0; g < 3; g++) {
        for (int j = 0; j < counts[g]; j++) {
            total += groups[g][j].count;
        }
    }
    /* 3+2+1+3+2+1 = 12 */
    if (total != 12) return 9;

    /* Test 5: simple int pointer array */
    if (ptrs[0] == 0) return 10;
    if (ptrs[0][0] != 1) return 11;
    if (ptrs[1][1] != 5) return 12;

    printf("ok\n");
    return 0;
}
