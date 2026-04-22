/* Test: global integer variable initialized from implicit float constant expression
 * Mirrors hexen/am_map.c: static fixed_t scale_mtof = (.2*FRACUNIT)
 * where FRACUNIT=65536 makes .2*FRACUNIT a float literal expression.
 * clang: accepts (evaluates to 13107), jmcc arm64: fails without cast.
 */
typedef int fixed_t;
#define FRACUNIT 65536
#define INITSCALEMTOF (.2*FRACUNIT)

static fixed_t scale_mtof = INITSCALEMTOF;

int main(void) {
    return scale_mtof != 13107;
}
