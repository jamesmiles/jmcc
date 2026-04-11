// TEST: ptr_member_index_submember
// DESCRIPTION: ptr->ptr_member[i].field must dereference ptr_member then index then access field
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's M_Drawer does:
     currentMenu->menuitems[i].name[0]
   currentMenu is menu_t*, menuitems is menuitem_t* (pointer member),
   [i] indexes the pointed-to array, .name[0] accesses a char array
   member of the i-th element.

   The access chain: ptr -> deref_ptr_member -> array_index -> field
   This crashes because the ptr_member dereference or the subsequent
   indexing computes a wrong address. */

int printf(const char *fmt, ...);

typedef struct {
    int status;
    char name[10];
} item_t;

typedef struct {
    short count;
    item_t *items;
    short x;
    short y;
} menu_t;

item_t my_items[] = {
    {1, "NewGame"},
    {1, "Options"},
    {1, "Quit"},
};

menu_t my_menu = {3, my_items, 100, 50};

int main(void) {
    menu_t *cur = &my_menu;
    short i;

    /* ptr->ptr_member[i].field */
    for (i = 0; i < cur->count; i++) {
        if (!cur->items[i].name[0])
            return 10 + i;
    }

    if (cur->items[0].name[0] != 'N') return 1;
    if (cur->items[1].name[0] != 'O') return 2;
    if (cur->items[2].status != 1) return 3;

    printf("ok\n");
    return 0;
}
