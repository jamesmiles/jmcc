// TEST: sys_stat_macros
// DESCRIPTION: sys/stat.h must provide S_ISDIR/S_ISREG/S_ISLNK macros
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* sys/stat.h defines S_ISDIR(m), S_ISREG(m), S_ISLNK(m) etc. as macros
   that test specific bits of st_mode. SQLite uses these extensively
   for file type checks. jmcc's built-in sys/stat.h doesn't define
   them, so they become undefined references at link time. */

#include <sys/stat.h>

int printf(const char *fmt, ...);

int main(void) {
    struct stat st;
    st.st_mode = 0040000;  /* typical S_IFDIR value */

    /* If these are function-call expressions instead of macros,
       the test will fail to link ("undefined reference to S_ISDIR"). */
    int is_dir = S_ISDIR(st.st_mode);
    int is_reg = S_ISREG(st.st_mode);
    int is_lnk = S_ISLNK(st.st_mode);

    (void)is_dir; (void)is_reg; (void)is_lnk;

    printf("ok\n");
    return 0;
}
