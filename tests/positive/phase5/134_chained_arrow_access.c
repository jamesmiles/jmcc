// TEST: chained_arrow_access
// DESCRIPTION: Chained pointer dereference ptr->member_ptr->field must work
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's renderer uses chained arrow access extensively:
     curline->sidedef->midtexture
     curline->linedef->flags
     curline->v1->y
   Each arrow dereferences a pointer, yielding another pointer
   or a value. The intermediate pointer must be loaded as 8 bytes. */

int printf(const char *fmt, ...);

struct vertex { int x; int y; };
struct side { int textureoffset; int rowoffset; int midtexture; };
struct line { int flags; struct side *sidedef; };

struct seg {
    struct vertex *v1;
    struct vertex *v2;
    struct line *linedef;
    struct side *sidedef;
};

int main(void) {
    struct vertex v1 = {100, 200};
    struct vertex v2 = {300, 400};
    struct side sd = {10, 20, 42};
    struct line ld = {0x1234, &sd};
    struct seg s = {&v1, &v2, &ld, &sd};
    struct seg *curline = &s;

    /* Single arrow */
    if (curline->sidedef->midtexture != 42) return 1;

    /* Double chain */
    if (curline->linedef->flags != 0x1234) return 2;

    /* Triple chain */
    if (curline->linedef->sidedef->rowoffset != 20) return 3;

    /* Vertex access */
    if (curline->v1->y != 200) return 4;
    if (curline->v2->x != 300) return 5;

    /* Comparison of chained values */
    if (curline->v1->y == curline->v2->y) return 6;
    if (curline->v1->x == curline->v2->x) return 7;

    /* Chained access used in array index */
    int table[50];
    table[42] = 999;
    int val = table[curline->sidedef->midtexture];
    if (val != 999) return 8;

    printf("ok\n");
    return 0;
}
