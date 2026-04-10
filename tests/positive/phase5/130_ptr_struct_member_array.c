// TEST: ptr_struct_member_array
// DESCRIPTION: ptr_to_struct[i].array_member[j] must index correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom uses: lumpinfo[l].name[4] where lumpinfo is lumpinfo_t*
   (pointer, not array). The access is ptr[i].member[j]. The stride
   for ptr[i] must be sizeof(lumpinfo_t), then offset to name member,
   then index by j with stride 1 (char). */

int printf(const char *fmt, ...);

typedef struct {
    char name[8];
    int handle;
    int position;
    int size;
} lumpinfo_t;

lumpinfo_t data[] = {
    {"TROOA0B0", 0, 0, 100},
    {"SHTGA0B0", 1, 100, 200},
    {"PUNGA0B0", 2, 300, 150},
};

lumpinfo_t *lumpinfo = data;

int main(void) {
    /* ptr[i].name[j] */
    if (lumpinfo[0].name[0] != 'T') return 1;
    if (lumpinfo[0].name[4] != 'A') return 2;
    if (lumpinfo[1].name[0] != 'S') return 3;
    if (lumpinfo[1].name[4] != 'A') return 4;
    if (lumpinfo[2].name[4] != 'A') return 5;

    /* The Doom pattern */
    int l = 1;
    int frame = lumpinfo[l].name[4] - 'A';
    if (frame != 0) return 6;

    int rotation = lumpinfo[l].name[5] - '0';
    if (rotation != 0) return 7;  /* '0' - '0' = 0 */

    /* Check truthiness of name[6] */
    if (lumpinfo[0].name[6] != 'B') return 8;

    /* Variable index for both */
    l = 2;
    int j = 5;
    char c = lumpinfo[l].name[j];
    if (c != '0') return 9;

    /* Struct fields after name */
    if (lumpinfo[1].handle != 1) return 10;
    if (lumpinfo[2].size != 150) return 11;

    printf("ok\n");
    return 0;
}
