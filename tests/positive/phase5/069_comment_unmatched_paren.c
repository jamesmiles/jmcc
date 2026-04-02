// TEST: comment_unmatched_paren
// DESCRIPTION: Unmatched paren in // comment must not collapse subsequent header lines
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: vol=8
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

/* Doom's doomstat.h has '//  (e.g. no sound volume adjustment with menu.'
   The unmatched '(' in the comment triggers the multi-line macro arg joiner,
   which collapses all subsequent lines into the comment line.
   This makes all type/function declarations after the comment invisible. */
#include "069_comment_unmatched_paren.h"

int get_default_volume(void) {
    return 8;
}

int main(void) {
    sound_config_t cfg;
    cfg.sfx_volume = get_default_volume();
    printf("vol=%d\n", cfg.sfx_volume);
    return 0;
}
