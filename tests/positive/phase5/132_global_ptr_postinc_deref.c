// TEST: global_ptr_postinc_deref
// DESCRIPTION: *global_ptr++ must dereference then increment correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's demo playback does:
     byte *demo_p;  (global)
     if (*demo_p++ != VERSION) ...
     skill = *demo_p++;
     episode = *demo_p++;
   Each *demo_p++ must read one byte then advance demo_p by 1.
   If the increment is wrong (e.g., advances by sizeof(byte*) = 8
   instead of 1), the subsequent reads get wrong data. */

int printf(const char *fmt, ...);

typedef unsigned char byte;

byte data[] = {110, 3, 1, 1, 0, 0, 0, 0};
byte *demo_p;

int main(void) {
    demo_p = data;

    /* *demo_p++ reads 110 and advances by 1 */
    int version = *demo_p++;
    if (version != 110) return 1;
    if (demo_p != &data[1]) return 2;

    /* Read next 3 bytes */
    int skill = *demo_p++;
    int episode = *demo_p++;
    int map = *demo_p++;

    if (skill != 3) return 3;
    if (episode != 1) return 4;
    if (map != 1) return 5;
    if (demo_p != &data[4]) return 6;

    /* Signed char cast pattern (Doom's ticcmd reads) */
    byte movement_data[] = {200, 50, 128, 0};
    demo_p = movement_data;

    signed char fwd = (signed char)*demo_p++;
    if (fwd != -56) return 7;  /* 200 as signed char = -56 */
    if (demo_p != &movement_data[1]) return 8;

    printf("ok\n");
    return 0;
}
