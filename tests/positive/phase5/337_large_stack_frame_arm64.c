/* Regression: function with local array larger than 4095 bytes.
 *
 * jmcc emits:  sub sp, sp, #4200
 * ARM64 error: "expected compatible register, symbol or integer in range [0, 4095]"
 *
 * The sub/add sp immediate is limited to 12-bit unsigned (0-4095).
 * For frames > 4095 bytes jmcc must either:
 *   (a) emit two sub instructions: sub sp, sp, #4096; sub sp, sp, #104
 *   (b) load the constant into a scratch register and use sub sp, sp, xN
 *
 * Triggered by src/gusconf.c (_GUS_WriteConfig, 4128-byte frame) and
 * src/hexen/sv_save.c (_SV_LoadGame, 5648-byte frame) in Chocolate Doom.
 */
#include <string.h>

int sum_large_buf(void) {
    char buf[4200]; /* forces frame > 4095 bytes */
    memset(buf, 0, sizeof(buf));
    buf[0]    = 1;
    buf[4199] = 2;
    return (unsigned char)buf[0] + (unsigned char)buf[4199]; /* 3 */
}

int main(void) {
    return sum_large_buf() - 3;
}
