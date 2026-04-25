/* Regression: __uint128_t is a Darwin/arm64 128-bit integer type used in
 * NEON register state structs. It appears in stdlib.h -> signal.h -> mach/arm
 * include chain. jmcc must recognise __uint128_t as a built-in type specifier
 * on arm64-apple-darwin (even if it stores it as two 64-bit words internally).
 *
 * Mirrors the __darwin_arm_neon_state64 / __darwin_arm_neon_state structs
 * that block d_net.c, deh_cheat.c, deh_doom.c, and many other Doom files.
 */
typedef __uint128_t uint128_t;

struct neon_state64 {
    __uint128_t v[32];
    unsigned int fpsr;
    unsigned int fpcr;
};

struct neon_state {
    __uint128_t v[16];
    unsigned int fpscr;
};

int main(void) {
    struct neon_state64 ns64;
    struct neon_state ns;
    uint128_t x = 0;
    (void)ns64; (void)ns; (void)x;
    return 0;
}
