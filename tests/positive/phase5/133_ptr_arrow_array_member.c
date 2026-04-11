// TEST: ptr_arrow_array_member
// DESCRIPTION: ptr->array_member[i] must compute correct offset through pointer deref
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom uses patterns like node->children[side] where node is a
   pointer and children is an array member. The access requires:
   1. Load node pointer
   2. Add offset of children field
   3. Add index * element_size
   4. Load the value

   This tests various element types in the array member. */

int printf(const char *fmt, ...);

struct node {
    int x, y, dx, dy;
    int bbox[2][4];
    unsigned short children[2];
};

struct simple {
    int id;
    char name[8];
    int values[4];
};

int main(void) {
    struct node n;
    n.children[0] = 1000;
    n.children[1] = 2000;

    struct node *ptr = &n;

    /* ptr->array_member[i] with unsigned short */
    if (ptr->children[0] != 1000) return 1;
    if (ptr->children[1] != 2000) return 2;

    /* Variable index */
    int side = 1;
    if (ptr->children[side] != 2000) return 3;

    /* ptr->name[i] with char */
    struct simple s;
    s.name[0] = 'H';
    s.name[4] = 'X';
    s.values[0] = 10;
    s.values[3] = 40;

    struct simple *sp = &s;
    if (sp->name[0] != 'H') return 4;
    if (sp->name[4] != 'X') return 5;
    if (sp->values[0] != 10) return 6;
    if (sp->values[3] != 40) return 7;

    /* 2D array member: node->bbox[i][j] */
    n.bbox[0][0] = 100;
    n.bbox[1][3] = 999;
    if (ptr->bbox[0][0] != 100) return 8;
    if (ptr->bbox[1][3] != 999) return 9;

    printf("ok\n");
    return 0;
}
