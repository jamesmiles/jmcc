// TEST: 2d_uchar_array_unsigned
// DESCRIPTION: Reading unsigned char from 2D array must zero-extend, not sign-extend
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's gammatable[5][256] is a 2D unsigned char array.
   Reading gammatable[0][231] should return 232 (unsigned),
   but jmcc sign-extends it to -24 (signed).

   This causes UploadNewPalette to produce negative R/G/B values,
   which when shifted and OR'd into the palette entry produce
   0xFFxxxxxx instead of 0x00xxxxxx, turning blues into white/yellow.

   Test 102 fixed struct member loads and test 104 fixed pointer
   dereference, but 2D array element access still sign-extends. */

int printf(const char *fmt, ...);

typedef unsigned char byte;

byte table[2][4] = {
    {100, 127, 128, 255},
    {200, 230, 250, 128}
};

int main(void) {
    int val;

    /* Values < 128 should work either way */
    val = table[0][0];
    if (val != 100) return 1;
    val = table[0][1];
    if (val != 127) return 2;

    /* Values >= 128 must be unsigned (0-255), not sign-extended */
    val = table[0][2];
    if (val != 128) return 3;   /* fails if sign-extended: -128 */

    val = table[0][3];
    if (val != 255) return 4;   /* fails if sign-extended: -1 */

    val = table[1][0];
    if (val != 200) return 5;   /* fails if sign-extended: -56 */

    /* Arithmetic must treat as unsigned */
    int shifted = table[0][3] << 16;
    if (shifted != 0x00FF0000) return 6;  /* fails if -1 << 16 = 0xFFFF0000 */

    /* The Doom pattern: gamma lookup + shift + OR */
    int r = table[1][2];  /* 250 */
    int g = table[1][3];  /* 128 */
    int b = table[0][0];  /* 100 */
    int pixel = (r << 16) | (g << 8) | b;
    if (pixel != 0x00FA8064) return 7;  /* 0xFA=250, 0x80=128, 0x64=100 */

    printf("ok\n");
    return 0;
}
