// TEST: struct_array_elem_copy
// DESCRIPTION: array[i] = array[j] struct copy must work for structs with function pointers
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's m_menu.c does:
     MainMenu[readthis] = MainMenu[quitdoom];
   menuitem_t is 32 bytes with a function pointer member.
   This is a legitimate struct-by-value copy between array elements. */

int printf(const char *fmt, ...);

typedef struct {
    int status;
    char name[10];
    void (*routine)(int choice);
    char alphaKey;
} menuitem_t;

void handler_a(int c) {}
void handler_b(int c) {}

menuitem_t items[] = {
    {1, "NewGame", handler_a, 'n'},
    {1, "Options", handler_b, 'o'},
    {1, "QuitGame", handler_a, 'q'},
    {-1, "", 0, 0},
};

int main(void) {
    /* Copy array element to array element */
    items[3] = items[2];

    if (items[3].status != 1) return 1;
    if (items[3].routine != handler_a) return 2;
    if (items[3].alphaKey != 'q') return 3;

    /* Verify name copied */
    if (items[3].name[0] != 'Q') return 4;
    if (items[3].name[4] != 'G') return 5;

    /* Verify original unchanged */
    if (items[2].status != 1) return 6;

    /* Variable index */
    int i = 0;
    int j = 1;
    items[i] = items[j];
    if (items[0].routine != handler_b) return 7;
    if (items[0].alphaKey != 'o') return 8;

    printf("ok\n");
    return 0;
}
