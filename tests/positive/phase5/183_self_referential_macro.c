// TEST: self_referential_macro
// DESCRIPTION: Self-referential macros must not cause infinite expansion
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* glibc's dirent.h defines:
     enum { DT_UNKNOWN = 0, ... };
     #define DT_UNKNOWN DT_UNKNOWN
   This is valid C — the macro expands once, then the resulting token
   DT_UNKNOWN is "painted blue" (marked as the macro being expanded)
   and is not expanded again. jmcc's preprocessor lacks this guard
   and recurses infinitely. This blocks Chocolate Doom's i_glob.c. */

int printf(const char *fmt, ...);

/* Self-referential enum + macro (glibc pattern) */
enum {
    MY_UNKNOWN = 0,
    MY_REG = 1,
    MY_DIR = 2
};

#define MY_UNKNOWN MY_UNKNOWN
#define MY_REG     MY_REG
#define MY_DIR     MY_DIR

/* Self-referential variable macro */
#define STATUS STATUS
int STATUS = 42;

int main(void) {
    if (MY_UNKNOWN != 0) return 1;
    if (MY_REG != 1) return 2;
    if (MY_DIR != 2) return 3;

    int type = MY_UNKNOWN;
    if (type != 0) return 4;

    type = MY_DIR;
    if (type != 2) return 5;

    if (STATUS != 42) return 6;

    printf("ok\n");
    return 0;
}
