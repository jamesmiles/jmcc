// TEST: pointer_to_array_decl
// DESCRIPTION: Pointer-to-array declarator char (*name)[N] must parse
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Chocolate Doom's i_oplmusic.c declares:
     static char (*main_instr_names)[32];
   This is a pointer to an array of 32 chars — used to point into
   an array of fixed-size name strings. jmcc can't parse the
   parenthesized pointer-to-array declarator. */

int printf(const char *fmt, ...);
int strcmp(const char *a, const char *b);

/* Array of fixed-size strings */
char names[3][16] = {"alpha", "beta", "gamma"};

/* Pointer to array of 16 chars */
char (*name_ptr)[16];

/* In a struct */
typedef struct {
    char (*labels)[32];
    int count;
} label_set_t;

int main(void) {
    /* Test 1: basic pointer to array */
    name_ptr = names;
    if (strcmp(name_ptr[0], "alpha") != 0) return 1;
    if (strcmp(name_ptr[1], "beta") != 0) return 2;
    if (strcmp(name_ptr[2], "gamma") != 0) return 3;

    /* Test 2: pointer arithmetic */
    name_ptr = &names[1];
    if (strcmp(name_ptr[0], "beta") != 0) return 4;

    /* Test 3: in a struct */
    char items[2][32] = {"first item", "second item"};
    label_set_t ls;
    ls.labels = items;
    ls.count = 2;
    if (strcmp(ls.labels[0], "first item") != 0) return 5;
    if (strcmp(ls.labels[1], "second item") != 0) return 6;

    /* Test 4: sizeof */
    if (sizeof(*name_ptr) != 16) return 7;

    printf("ok\n");
    return 0;
}
