// TEST: double_ptr_struct_stride
// DESCRIPTION: Indexing struct_t** must use sizeof(pointer) stride, not sizeof(struct)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's textures is texture_t** — an array of pointers to texture_t.
   Indexing textures[i] must advance by sizeof(texture_t*) = 8 bytes,
   not sizeof(texture_t).  When sizeof(struct) < 8, using the struct
   size as stride reads from the wrong address, causing a crash in
   R_GenerateLookup when it dereferences corrupted texture pointers. */

int printf(const char *fmt, ...);
void *malloc(unsigned long);

typedef struct { short a; short b; } Small;

int main(void) {
    Small **arr = malloc(3 * sizeof(Small*));
    for (int i = 0; i < 3; i++) {
        arr[i] = malloc(sizeof(Small));
        arr[i]->a = (i + 1) * 10;
        arr[i]->b = (i + 1) * 20;
    }

    if (arr[0]->a != 10) return 1;
    if (arr[1]->a != 20) return 2;
    if (arr[2]->a != 30) return 3;

    printf("ok\n");
    return 0;
}
