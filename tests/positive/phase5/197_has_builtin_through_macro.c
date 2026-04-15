// TEST: has_builtin_through_macro
// DESCRIPTION: __has_builtin must work when invoked through a macro wrapper
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SDL_stdinc.h wraps __has_builtin in a helper macro:
     #ifdef __has_builtin
     #define _SDL_HAS_BUILTIN(x) __has_builtin(x)
     #else
     #define _SDL_HAS_BUILTIN(x) 0
     #endif
   Then uses it in conditions like:
     #if _SDL_HAS_BUILTIN(__builtin_bswap32)
   jmcc's __has_builtin works when used DIRECTLY in #if, but when
   wrapped in a macro it evaluates to 0/false. This is why Chocolate
   Doom still has no music even after __has_builtin support landed —
   SDL always goes through the macro wrapper. */

int printf(const char *fmt, ...);

#ifdef __has_builtin
#define MY_HAS_BUILTIN(x) __has_builtin(x)
#else
#define MY_HAS_BUILTIN(x) 0
#endif

int main(void) {
    /* Test 1: direct __has_builtin in #if */
#if __has_builtin(__builtin_bswap32)
    int direct = 1;
#else
    int direct = 0;
#endif

    /* Test 2: via macro wrapper — must match direct */
#if MY_HAS_BUILTIN(__builtin_bswap32)
    int via_macro = 1;
#else
    int via_macro = 0;
#endif

    if (direct != via_macro) return 1;
    if (direct != 1) return 2;  /* jmcc supports __builtin_bswap32 */

    printf("ok\n");
    return 0;
}
