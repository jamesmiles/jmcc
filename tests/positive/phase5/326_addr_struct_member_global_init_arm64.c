/* Test: address of struct member used as global initializer value.
 *
 * Reproduces the pattern from Chocolate Doom's DEH_BEGIN_MAPPING /
 * DEH_MAPPING macros (deh_mapping.h), which expand to a static struct
 * global whose fields are initialised with &base_struct.fieldname.
 *
 * clang: OK
 * jmcc (arm64-apple-darwin): error: does not yet support this global
 *   initializer value  (arm64 backend cannot emit field-address relocations)
 */

#include <stddef.h>

/* Miniature version of the state_t / deh_mapping_t pattern from Doom */
typedef struct {
    int sprite;
    int frame;
    int tics;
} state_t;

typedef struct {
    const char *name;
    int        *field_ptr;
    int         size;
    int         is_string;
} mapping_entry_t;

typedef struct {
    state_t         *base;
    mapping_entry_t  entries[4];
} mapping_t;

static state_t deh_mapping_base;

/* Each entry uses &deh_mapping_base.field — an address-of-struct-member
 * constant expression that requires a relocation at link time. */
static mapping_t state_mapping = {
    &deh_mapping_base,
    {
        {"Sprite number",    &deh_mapping_base.sprite, sizeof(deh_mapping_base.sprite), 0},
        {"Sprite subnumber", &deh_mapping_base.frame,  sizeof(deh_mapping_base.frame),  0},
        {"Duration",         &deh_mapping_base.tics,   sizeof(deh_mapping_base.tics),   0},
        {NULL, NULL, -1, 0}
    }
};

int main(void) {
    /* Sanity-check the generated mapping at run time */
    if (state_mapping.base != &deh_mapping_base)
        return 1;
    if (state_mapping.entries[0].field_ptr != &deh_mapping_base.sprite)
        return 2;
    if (state_mapping.entries[1].size != (int)sizeof(int))
        return 3;
    return 0;
}
