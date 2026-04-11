// TEST: ptr_array_member_chain
// DESCRIPTION: ptr->ptr_array[i]->member chain must dereference correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's HUD code does:
     w = SHORT(l->f[c - l->sc]->width);
   l is hu_textline_t*, f is patch_t** (pointer array member),
   [c-sc] indexes into the array, then ->width accesses the patch.

   This is a 3-level chain: ptr->ptr_array_member[i]->field
   Each intermediate pointer must be loaded as 8 bytes. */

int printf(const char *fmt, ...);

struct patch {
    short width;
    short height;
};

struct textline {
    int sc;
    struct patch **f;  /* array of patch pointers */
    char l[80];
    int len;
};

struct patch patches[3] = {{10, 20}, {30, 40}, {50, 60}};
struct patch *patch_ptrs[3] = {&patches[0], &patches[1], &patches[2]};

int main(void) {
    struct textline t;
    t.sc = 'A';  /* start char */
    t.f = patch_ptrs;

    struct textline *l = &t;

    /* l->f[c - l->sc]->width */
    char c = 'B';  /* index = 'B' - 'A' = 1 */
    short w = l->f[c - l->sc]->width;
    if (w != 30) return 1;

    c = 'C';  /* index = 2 */
    w = l->f[c - l->sc]->width;
    if (w != 50) return 2;

    /* Also test height */
    short h = l->f[0]->height;
    if (h != 20) return 3;

    printf("ok\n");
    return 0;
}
