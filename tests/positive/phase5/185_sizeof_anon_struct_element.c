// TEST: sizeof_anon_struct_element
// DESCRIPTION: sizeof element of anonymous struct array must include all fields
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Chocolate Doom's w_main.c declares:
     static const struct { GameMission_t mission; const char *lumpname; }
         unique_lumps[] = { {doom, "POSSA1"}, ... };
   Then uses arrlen(unique_lumps) which is sizeof(arr)/sizeof(arr[0]).
   jmcc evaluates sizeof(unique_lumps[0]) as 4 (just the int field)
   instead of 16 (int + padding + pointer). This causes the iteration
   loop to run 16 times instead of 4, reading past the array and
   crashing with a NULL pointer. */

int printf(const char *fmt, ...);

/* Anonymous struct array — Chocolate Doom's exact pattern */
static const struct {
    int id;
    const char *name;
} items[] = {
    { 1, "alpha" },
    { 2, "beta" },
    { 3, "gamma" },
};

/* Chocolate Doom uses sizeof(*array) not sizeof(array[0]) */
#define arrlen(x) (sizeof(x) / sizeof(*x))

/* Another variant: mixed int and pointer */
static struct {
    int type;
    void *data;
    int count;
} entries[] = {
    { 0, 0, 10 },
    { 1, 0, 20 },
};

int main(void) {
    /* Test 1: sizeof element must include pointer */
    if (sizeof(items[0]) != 16) return 1;  /* int(4) + pad(4) + ptr(8) = 16 */

    /* Test 2: sizeof array / sizeof element = element count */
    if (arrlen(items) != 3) return 2;

    /* Test 3: verify we can iterate correctly */
    int i;
    int total = 0;
    for (i = 0; i < arrlen(items); i++)
        total += items[i].id;
    if (total != 6) return 3;

    /* Test 4: access string members */
    if (items[0].name[0] != 'a') return 4;
    if (items[2].name[0] != 'g') return 5;

    /* Test 5: three-field struct */
    if (sizeof(entries[0]) != 24) return 6;  /* int(4) + pad(4) + ptr(8) + int(4) + pad(4) = 24 */
    if (arrlen(entries) != 2) return 7;

    /* Test 6: iteration with arrlen on three-field struct */
    total = 0;
    for (i = 0; i < arrlen(entries); i++)
        total += entries[i].count;
    if (total != 30) return 8;

    printf("ok\n");
    return 0;
}
