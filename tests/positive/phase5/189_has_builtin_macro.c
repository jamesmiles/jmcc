// TEST: has_builtin_macro
// DESCRIPTION: __has_builtin must be supported (C2x / GCC extension)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SDL2's SDL_endian.h checks __has_builtin(__builtin_bswap32) to
   decide whether to use the builtin or fall back to inline asm.
   jmcc supports __builtin_bswap32 (test 188), but doesn't support
   __has_builtin so SDL takes the asm path. jmcc skips asm, so
   byteswap functions return their input unchanged, breaking MIDI
   parsing in Chocolate Doom (no music).

   Fix: jmcc preprocessor must support __has_builtin so SDL headers
   discover the available builtins automatically. */

int printf(const char *fmt, ...);

int main(void) {
#if defined(__has_builtin)
    /* __has_builtin is supported as a preprocessor function */
#  if __has_builtin(__builtin_bswap32)
    if (__builtin_bswap32(0x12345678U) != 0x78563412U)
        return 1;
#  else
    return 2;
#  endif
#  if __has_builtin(__builtin_bswap16)
    if (__builtin_bswap16(0x1234) != 0x3412)
        return 3;
#  endif
#else
    /* __has_builtin not even defined */
    return 4;
#endif

    printf("ok\n");
    return 0;
}
