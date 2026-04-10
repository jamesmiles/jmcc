// TEST: truecolor_palette_convert
// DESCRIPTION: 8-bit indexed to 32-bit ARGB conversion must produce correct pixels
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's TrueColor I_FinishUpdate converts an 8-bit indexed framebuffer
   (screens[0]) to 32-bit ARGB pixels in the XImage buffer using a
   palette lookup table (rgb_palette[256]).

   Key requirements:
   - Source and destination buffers must be SEPARATE (screens[0] is 1 byte/pixel,
     output is 4 bytes/pixel — aliasing them corrupts the conversion)
   - Each source byte indexes into rgb_palette to produce a 32-bit pixel
   - With multiply > 1, each source pixel is replicated m*m times */

int printf(const char *fmt, ...);

/* Simulate the I_FinishUpdate conversion */
void convert_framebuffer(
    unsigned char *src,    /* 8-bit indexed, SCREENWIDTH * SCREENHEIGHT */
    unsigned int *dst,     /* 32-bit ARGB, width * height * multiply^2 */
    unsigned int *palette, /* 256-entry palette */
    int sw, int sh,        /* source dimensions */
    int multiply)
{
    int x, y, row, col;
    for (y = 0; y < sh; y++)
    {
        for (row = 0; row < multiply; row++)
        {
            for (x = 0; x < sw; x++)
            {
                unsigned int pixel = palette[src[y * sw + x]];
                for (col = 0; col < multiply; col++)
                    *dst++ = pixel;
            }
        }
    }
}

int main(void) {
    /* Small test framebuffer: 4x2 pixels */
    unsigned char src[8] = {0, 1, 2, 3, 4, 5, 6, 7};
    unsigned int palette[256];
    unsigned int dst[8];
    int i;

    /* Set up palette: index i -> 0xAA000000 | (i * 0x010101) */
    for (i = 0; i < 256; i++)
        palette[i] = 0xAA000000 | (i * 0x010101);

    /* Test 1: multiply=1 conversion */
    for (i = 0; i < 8; i++) dst[i] = 0;
    convert_framebuffer(src, dst, palette, 4, 2, 1);

    if (dst[0] != 0xAA000000) return 1;
    if (dst[1] != 0xAA010101) return 2;
    if (dst[7] != 0xAA070707) return 3;

    /* Test 2: source and dest must be separate buffers.
       If they alias (like the bug), src gets overwritten by first
       dst write and subsequent reads get garbage. */
    {
        /* Simulate the bug: alias src to dst */
        unsigned char buf[32];  /* shared buffer */
        unsigned char *bad_src = buf;
        unsigned int *bad_dst = (unsigned int *)buf;

        bad_src[0] = 1;
        bad_src[1] = 2;
        bad_src[2] = 3;
        bad_src[3] = 4;

        /* First pixel conversion overwrites bytes 0-3 */
        bad_dst[0] = palette[bad_src[0]];  /* writes 4 bytes at buf[0..3] */
        /* Now bad_src[1] is corrupted! */
        unsigned int second = palette[bad_src[1]];
        /* bad_src[1] was 2, but after the write it's been overwritten */
        if (second == palette[2]) {
            /* This would only work if the write didn't clobber src[1],
               which is impossible when aliased */
            printf("ok (aliased - unexpected)\n");
        }
        /* The aliased conversion produces wrong results */
        if (second != palette[2]) {
            /* Expected: aliased buffer is corrupted */
        }
    }

    /* Test 3: multiply=2 conversion */
    {
        unsigned int dst2x[32];  /* 8x4 = 32 pixels */
        unsigned char src2[8] = {10, 20, 30, 40, 50, 60, 70, 80};
        convert_framebuffer(src2, dst2x, palette, 4, 2, 2);

        /* Row 0, first pass: pixel[0]=palette[10] twice, pixel[1]=palette[20] twice */
        if (dst2x[0] != palette[10]) return 4;
        if (dst2x[1] != palette[10]) return 5;  /* duplicated */
        if (dst2x[2] != palette[20]) return 6;
        if (dst2x[3] != palette[20]) return 7;

        /* Row 0, second pass (duplicate of first): same pixels */
        if (dst2x[8] != palette[10]) return 8;

        /* Row 1: starts at pixel 16 (4*2 * 2 rows) */
        if (dst2x[16] != palette[50]) return 9;
    }

    printf("ok\n");
    return 0;
}
