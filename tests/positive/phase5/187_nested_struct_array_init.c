// TEST: nested_struct_array_init
// DESCRIPTION: Struct containing array of structs must fully initialize all fields
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Chocolate Doom's DEH_MAPPING macro creates:
     static mapping_t state_mapping = {
         &deh_mapping_base,
         {
             {"Sprite number", &base.sprite, sizeof(base.sprite), 0},
             {"Sprite subnumber", &base.frame, sizeof(base.frame), 0},
             ...
         }
     };
   jmcc only emits the first field (name) of each inner struct and
   zeros for the rest. This causes runtime "Unknown dehacked mapping
   field type" error because entry->size is 0 instead of 4. */

int printf(const char *fmt, ...);

typedef struct {
    const char *name;
    int offset;
    int size;
    int flag;
} entry_t;

typedef struct {
    void *base;
    entry_t entries[4];
} mapping_t;

static int some_global = 0;

/* Nested init: outer struct with array of inner structs */
static mapping_t mapping = {
    &some_global,
    {
        {"first",  1, 10, 0},
        {"second", 2, 20, 1},
        {"third",  3, 30, 0},
        {"fourth", 4, 40, 1}
    }
};

int main(void) {
    /* Test 1: base pointer */
    if (mapping.base != &some_global) return 1;

    /* Test 2: first entry all fields */
    if (mapping.entries[0].name[0] != 'f') return 2;
    if (mapping.entries[0].offset != 1) return 3;
    if (mapping.entries[0].size != 10) return 4;
    if (mapping.entries[0].flag != 0) return 5;

    /* Test 3: second entry */
    if (mapping.entries[1].offset != 2) return 6;
    if (mapping.entries[1].size != 20) return 7;
    if (mapping.entries[1].flag != 1) return 8;

    /* Test 4: fourth entry */
    if (mapping.entries[3].offset != 4) return 9;
    if (mapping.entries[3].size != 40) return 10;
    if (mapping.entries[3].flag != 1) return 11;

    printf("ok\n");
    return 0;
}
