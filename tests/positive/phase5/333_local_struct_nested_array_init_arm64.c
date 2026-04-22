/* Regression: local struct variable initialised with a nested array initialiser
 * must work on arm64-apple-darwin.
 *
 * Mirrors wi_stuff.c in Chocolate Doom:
 *
 *   patch_t tmp = { SCREENWIDTH, SCREENHEIGHT, 1, 1,
 *                   { 0, 0, 0, 0, 0, 0, 0, 0 } };
 *
 * where patch_t contains a short[] field. The backend must handle an InitList
 * node appearing as the last element of a local struct initialiser
 * (distinct from test 330 which covers global struct + nested array init).
 */

typedef struct {
    int width;
    int height;
    int x;
    int y;
    short data[8];
} patch_t;

static void use_patch(patch_t *p) { (void)p; }

void init_patch(int w, int h) {
    patch_t tmp = { w, h, 1, 1, { 0, 0, 0, 0, 0, 0, 0, 0 } };
    use_patch(&tmp);
}

int main(void) {
    init_patch(320, 200);
    return 0;
}
