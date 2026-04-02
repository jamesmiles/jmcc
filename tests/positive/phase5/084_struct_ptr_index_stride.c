// TEST: struct_ptr_index_stride
// DESCRIPTION: Pointer-to-struct indexing must use sizeof(struct) as stride, not sizeof(first member)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's W_AddFile loops over filelump_t* with fileinfo[i].filepos etc.
   filelump_t is { int filepos; int size; char name[8]; } = 16 bytes.
   If ptr[i] uses the wrong stride (e.g. 4 instead of sizeof(struct)),
   it reads from the wrong offset, corrupting lump positions/sizes and
   causing R_InitTextures to compute a bogus allocation size. */

int printf(const char *fmt, ...);

typedef struct { int x; int y; } Point;

int main(void) {
    Point pts[3] = {{10, 20}, {30, 40}, {50, 60}};
    Point *p = pts;

    if (p[0].x != 10) return 1;
    if (p[0].y != 20) return 1;
    if (p[1].x != 30) return 1;
    if (p[1].y != 40) return 1;
    if (p[2].x != 50) return 1;
    if (p[2].y != 60) return 1;

    printf("ok\n");
    return 0;
}
