// TEST: asm_statement
// DESCRIPTION: __asm__ statements must be accepted (parsed and skipped)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SDL's byte-swapping headers (SDL_endian.h) contain inline asm:
     __asm__("xchgb %b0,%h0": "=Q"(x):"0"(x));
   jmcc doesn't need to execute inline asm, but it must parse and
   skip these statements to compile any code that includes SDL.h.
   Both __asm__ and asm keywords should be accepted. */

int printf(const char *fmt, ...);

int add_pure_c(int a, int b) {
    return a + b;
}

/* Function containing asm that jmcc should skip over */
static inline int swap16(int x) {
    /* jmcc should parse and ignore this */
    __asm__("" : : : "memory");
    return x;
}

int main(void) {
    /* Only test the pure C function */
    if (add_pure_c(3, 4) != 7) return 1;
    printf("ok\n");
    return 0;
}
