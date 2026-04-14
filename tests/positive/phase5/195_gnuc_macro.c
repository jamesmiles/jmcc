// TEST: gnuc_macro
// DESCRIPTION: jmcc must define __GNUC__ (and __GNUC_MINOR__) since it supports GNU extensions
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Many headers gate GNU extensions on #if defined(__GNUC__).
   SDL2's SDL_endian.h does this for the __builtin_bswap path:
     #if defined(__GNUC__) || defined(__clang__)
     #   define HAS_BUILTIN_BSWAP32 (_SDL_HAS_BUILTIN(__builtin_bswap32)) || ...
     #endif
   Without __GNUC__ defined, SDL_Swap32 falls back to inline asm.
   jmcc skips asm, so SDL_Swap32 returns input unchanged, breaking
   MIDI parsing in Chocolate Doom (no music).

   jmcc supports __extension__, __attribute__, __asm__ (skip),
   __restrict, __builtin_bswap, statement expressions, etc.
   It SHOULD define __GNUC__ to advertise this. */

int printf(const char *fmt, ...);

int main(void) {
#if defined(__GNUC__)
    /* good — jmcc defines __GNUC__ */
#  if defined(__GNUC_MINOR__)
    /* even better */
#  else
    return 2;  /* __GNUC__ defined but not __GNUC_MINOR__ */
#  endif
#else
    return 1;  /* __GNUC__ not defined */
#endif

    printf("ok\n");
    return 0;
}
