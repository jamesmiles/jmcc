// TEST: cmdline_define
// DESCRIPTION: Compiler -D flag to define macros (Doom requires -DNORMALUNIX)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5
// DEFINES: NORMALUNIX LINUX

int printf(const char *fmt, ...);

/* Doom's d_main.c wraps system includes in #ifdef NORMALUNIX.
   The original Makefile passes -DNORMALUNIX -DLINUX on the command line.
   JMCC needs -D flag support to compile Doom. */

#ifdef NORMALUNIX
int mode = 1;
#else
int mode = 0;
#endif

int main(void) {
    /* Without -DNORMALUNIX, mode will be 0 and this test fails */
    if (mode == 1) {
        printf("ok\n");
    } else {
        printf("FAIL: NORMALUNIX not defined\n");
    }
    return mode == 1 ? 0 : 1;
}
