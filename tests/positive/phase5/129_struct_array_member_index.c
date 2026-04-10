// TEST: struct_array_member_index
// DESCRIPTION: Indexing into a char array member of a struct array element must work
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's R_InitSpriteDefs accesses:
     lumpinfo[l].name[4]
   where lumpinfo is an array of structs and name is a char[8] member.
   The double subscript (array_of_structs[i].array_member[j]) requires
   first computing &lumpinfo[l] (struct stride), then offsetting to
   the name field, then indexing with [4] (byte stride). */

int printf(const char *fmt, ...);

struct lumpinfo_t {
    char name[8];
    int handle;
    int position;
    int size;
};

struct lumpinfo_t lumps[] = {
    {"TROOABCD", 0, 0, 100},
    {"SHTGEFGH", 1, 100, 200},
    {"PUNGIJKL", 2, 300, 150},
};

int main(void) {
    /* Basic member access */
    if (lumps[0].name[0] != 'T') return 1;
    if (lumps[0].name[4] != 'A') return 2;

    /* Second element */
    if (lumps[1].name[0] != 'S') return 3;
    if (lumps[1].name[4] != 'E') return 4;

    /* The Doom pattern: frame = name[4] - 'A' */
    int frame = lumps[2].name[4] - 'A';
    if (frame != 8) return 5;  /* 'I' - 'A' = 8 */

    /* Variable index */
    int l = 1;
    if (lumps[l].name[5] != 'F') return 6;

    /* Truthiness check on name[6] */
    if (!lumps[0].name[6]) return 7;  /* 'C' is truthy */

    /* Struct field after name */
    if (lumps[1].handle != 1) return 8;
    if (lumps[2].size != 150) return 9;

    printf("ok\n");
    return 0;
}
