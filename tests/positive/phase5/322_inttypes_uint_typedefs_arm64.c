/* Regression: inttypes.h must make uint8_t/uint16_t/uint32_t/uint64_t available
 * as type names. On macOS the real stdint.h uses complex __attribute__ chains
 * that jmcc's preprocessor must resolve so downstream typedefs work.
 * Mirrors doomtype.h: typedef uint8_t byte; typedef uint16_t dpixel_t; etc.
 */
#include <inttypes.h>

typedef uint8_t  byte;
typedef uint8_t  pixel_t;
typedef uint16_t dpixel_t;
typedef uint32_t fixed_t;
typedef int64_t  ticcmd_t_pad;

int main(void) {
    byte b = 255;
    pixel_t p = 0;
    dpixel_t d = 1000;
    fixed_t f = 65536;
    ticcmd_t_pad t = -1;
    (void)(b + p + d + f + t);
    return 0;
}
