// TEST: uchar_ptr_deref_unsigned
// DESCRIPTION: Dereferencing unsigned char pointer must zero-extend, not sign-extend
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's I_FinishUpdate does:
     byte *src = screens[0];  // byte = unsigned char
     unsigned int pixel = rgb_palette[src[y * 320 + x]];
   If src[i] with value 200 is sign-extended to -56 via movsbl,
   the palette index becomes negative, reading before the array.

   Test 102 fixed this for struct members. This tests pointer
   dereference: *(unsigned char *)ptr and ptr[index]. */

int printf(const char *fmt, ...);

typedef unsigned char byte;

int lookup[256];

int main(void) {
    int i;
    byte data[4] = {0, 127, 128, 255};
    byte *ptr = data;

    for (i = 0; i < 256; i++)
        lookup[i] = i * 10;

    /* Dereference via pointer index — must be 0..255, not negative */
    if (lookup[ptr[0]] != 0) return 1;
    if (lookup[ptr[1]] != 1270) return 2;
    if (lookup[ptr[2]] != 1280) return 3;   /* 128*10; fails if sign-extended: lookup[-128] */
    if (lookup[ptr[3]] != 2550) return 4;   /* 255*10; fails if sign-extended: lookup[-1] */

    /* Dereference via *ptr */
    ptr = &data[3];
    int val = *ptr;
    if (val != 255) return 5;  /* fails if sign-extended to -1 */

    /* Arithmetic on dereferenced unsigned char */
    ptr = &data[2];
    int product = *ptr * 320;
    if (product != 40960) return 6;  /* 128*320; fails if -128*320 = -40960 */

    printf("ok\n");
    return 0;
}
