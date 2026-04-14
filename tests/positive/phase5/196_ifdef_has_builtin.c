// TEST: ifdef_has_builtin
// DESCRIPTION: #ifdef __has_builtin must agree with #if defined(__has_builtin)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SDL_stdinc.h uses:
     #ifdef __has_builtin
     #define _SDL_HAS_BUILTIN(x) __has_builtin(x)
     #else
     #define _SDL_HAS_BUILTIN(x) 0
     #endif
   jmcc supports __has_builtin in #if expressions but #ifdef
   reports it as undefined, so SDL takes the "0" fallback path.
   This is why __has_builtin (test 189) passed but Chocolate Doom
   still has no music. The C standard requires #ifdef X and
   #if defined(X) to be equivalent. */

int printf(const char *fmt, ...);

int main(void) {
    /* Test 1: #ifdef should detect __has_builtin same as #if defined */
#ifdef __has_builtin
    int via_ifdef = 1;
#else
    int via_ifdef = 0;
#endif

#if defined(__has_builtin)
    int via_defined = 1;
#else
    int via_defined = 0;
#endif

    if (via_ifdef != via_defined) return 1;
    if (via_defined != 1) return 2;  /* defined() must also see it */

    /* Test 2: actually use it */
#if __has_builtin(__builtin_bswap32)
    if (__builtin_bswap32(0x12345678U) != 0x78563412U) return 3;
#else
    return 4;  /* should be available */
#endif

    printf("ok\n");
    return 0;
}
