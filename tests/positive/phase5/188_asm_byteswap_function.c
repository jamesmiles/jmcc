// TEST: asm_byteswap_function
// DESCRIPTION: Inline byteswap functions must work or jmcc must support __builtin_bswap
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SDL2's SDL_endian.h defines byteswap functions like SDL_Swap32 using
   inline asm: __asm__("bswap %0" : "=r"(x) : "0"(x));
   jmcc skips __asm__ statements (test 172), but for byteswap functions
   this means they return the input unchanged. SDL_SwapBE32(midi_size)
   doesn't actually swap bytes, so MIDI files fail to load and Chocolate
   Doom has no music.

   Two possible fixes:
   1. Implement __builtin_bswap16/32/64 — SDL falls back to these when
      __has_builtin reports them available
   2. Recognize the bswap asm pattern and emit equivalent C code

   The test uses __builtin_bswap32 which the compiler should support. */

int printf(const char *fmt, ...);

int main(void) {
    /* Test: __builtin_bswap32 */
    unsigned int x = 0x12345678;
    unsigned int swapped = __builtin_bswap32(x);
    if (swapped != 0x78563412) return 1;

    /* Round trip */
    if (__builtin_bswap32(swapped) != x) return 2;

    /* 16-bit */
    unsigned short s = 0x1234;
    if (__builtin_bswap16(s) != 0x3412) return 3;

    /* 64-bit */
    unsigned long long ll = 0x123456789abcdef0ULL;
    if (__builtin_bswap64(ll) != 0xf0debc9a78563412ULL) return 4;

    printf("ok\n");
    return 0;
}
