// TEST: ptr_plus_constant_stride
// DESCRIPTION: ptr + integer must scale by sizeof(*ptr), not add raw bytes
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's R_ClearClipSegs does: newend = solidsegs + 2;
   solidsegs is cliprange_t* (8 bytes per element). solidsegs + 2
   must advance by 2 * sizeof(cliprange_t) = 16 bytes, not 2 bytes.

   The compiler adds the raw integer without multiplying by element
   size, so newend points 2 bytes into the first entry instead of
   pointing to the third entry. This corrupts the clip segment list
   and crashes the BSP renderer. */

int printf(const char *fmt, ...);

struct pair { int first; int last; };

struct pair arr[10];

int main(void) {
    arr[0].first = 10; arr[0].last = 20;
    arr[1].first = 30; arr[1].last = 40;
    arr[2].first = 50; arr[2].last = 60;

    /* ptr + constant must scale by sizeof(struct pair) = 8 */
    struct pair *p = arr + 2;
    if (p->first != 50) return 1;
    if (p->last != 60) return 2;

    /* ptr + 1 */
    p = arr + 1;
    if (p->first != 30) return 3;

    /* Verify address math */
    long diff = (char *)(arr + 2) - (char *)arr;
    if (diff != 2 * sizeof(struct pair)) return 4;  /* should be 16 */

    /* With variable */
    int n = 3;
    arr[3].first = 70;
    p = arr + n;
    if (p->first != 70) return 5;

    /* Assign to global pointer (the Doom pattern) */
    struct pair *global_end;
    global_end = arr + 2;
    if (global_end->first != 50) return 6;

    printf("ok\n");
    return 0;
}
