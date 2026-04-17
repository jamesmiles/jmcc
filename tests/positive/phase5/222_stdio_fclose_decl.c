// TEST: stdio_fclose_decl
// DESCRIPTION: jmcc's bundled stdio.h must declare FILE* functions so they can be used as function pointers
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* jmcc's bundled stdio.h declares FILE, stdin/stdout/stderr and macros,
   but does NOT declare fopen/fclose/fgets/fputs/fread/fwrite/fseek/etc.
   Call sites work via implicit declaration, but taking the address of
   a stdio function (e.g. to store it as a callback) requires an
   explicit declaration.

   SQLite's shell.c stores fclose as a function-pointer closer:
       sCtx.xCloser = fclose;
   which errors as "undeclared variable 'fclose'" in jmcc. */

#include <stdio.h>

int main(void) {
    /* Use stdio functions as function pointers — requires declarations */
    int (*pclose)(FILE *) = fclose;
    FILE *(*popen_ptr)(const char *, const char *) = fopen;

    (void)pclose;
    (void)popen_ptr;

    /* Also: exercise common stdio calls */
    if (fputs("ok\n", stdout) < 0) return 1;
    return 0;
}
