// TEST: 2d_member_array_decay
// DESCRIPTION: ptr->array2d[i] must decay to pointer, not dereference first element
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom passes bsp->bbox[side] to R_CheckBBox(fixed_t *bspcoord).
   bbox is int[2][4]. bbox[side] should decay to int* (pointer to
   the 4-element inner array). But jmcc dereferences it, passing
   bbox[side][0] (an int value) instead of &bbox[side][0] (a pointer).
   R_CheckBBox then treats a small integer as a memory address → segfault. */

int printf(const char *fmt, ...);

int sum_array(int *arr, int n) {
    int total = 0;
    int i;
    for (i = 0; i < n; i++)
        total += arr[i];
    return total;
}

struct node {
    int x, y;
    int bbox[2][4];
};

int main(void) {
    struct node n;
    n.bbox[0][0] = 10; n.bbox[0][1] = 20; n.bbox[0][2] = 30; n.bbox[0][3] = 40;
    n.bbox[1][0] = 50; n.bbox[1][1] = 60; n.bbox[1][2] = 70; n.bbox[1][3] = 80;

    struct node *ptr = &n;

    /* ptr->bbox[0] must decay to int* pointing to {10,20,30,40} */
    int total = sum_array(ptr->bbox[0], 4);
    if (total != 100) return 1;  /* 10+20+30+40 */

    /* ptr->bbox[1] must decay to int* pointing to {50,60,70,80} */
    total = sum_array(ptr->bbox[1], 4);
    if (total != 260) return 2;  /* 50+60+70+80 */

    /* With variable index */
    int side = 1;
    total = sum_array(ptr->bbox[side], 4);
    if (total != 260) return 3;

    /* XOR index (Doom pattern) */
    side = 0;
    total = sum_array(ptr->bbox[side ^ 1], 4);
    if (total != 260) return 4;

    printf("ok\n");
    return 0;
}
