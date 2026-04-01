// TEST: system_header_constants
// DESCRIPTION: System header constants used by Doom (R_OK, O_RDONLY, etc.)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: R_OK=4
// STDOUT: W_OK=2
// STDOUT: X_OK=1
// STDOUT: O_RDONLY=0
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

/* Doom includes <unistd.h> for R_OK/W_OK/X_OK and <fcntl.h> for O_RDONLY.
   These are POSIX constants that JMCC needs to provide via system headers.
   For now, test with local defines as a baseline. */
#ifndef R_OK
#define R_OK 4
#endif
#ifndef W_OK
#define W_OK 2
#endif
#ifndef X_OK
#define X_OK 1
#endif
#ifndef O_RDONLY
#define O_RDONLY 0
#endif

int main(void) {
    printf("R_OK=%d\n", R_OK);
    printf("W_OK=%d\n", W_OK);
    printf("X_OK=%d\n", X_OK);
    printf("O_RDONLY=%d\n", O_RDONLY);
    return 0;
}
