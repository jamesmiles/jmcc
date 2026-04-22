/* Regression: array-of-struct field inside a struct global initialiser must work
 * on arm64-apple-darwin.
 *
 * Mirrors the deh_mapping_t pattern in Chocolate Doom's deh_mapping.h where
 * DEH_BEGIN_MAPPING expands to:
 *
 *   static deh_mapping_t state_mapping = {
 *       &deh_mapping_base,                   // void *base
 *       {                                    // entry_t entries[MAX_MAPPING_ENTRIES]
 *           { "field", &base.member, sizeof(...), 0 },
 *           { NULL, NULL, -1, 0 }
 *       }
 *   };
 *
 * The backend must be able to emit a global struct whose second field is an
 * inline array-of-structs initialiser (nested braces one level deeper).
 */
#include <stddef.h>

typedef struct {
    const char *name;
    int size;
} entry_t;

typedef struct {
    int count;
    entry_t entries[4];
} mapping_t;

static mapping_t m = {
    2,
    {
        { "alpha", 4 },
        { "beta",  8 },
        { NULL,   -1 }
    }
};

int main(void) {
    (void)m.count;
    (void)m.entries[0].name;
    (void)m.entries[2].size;
    return 0;
}
