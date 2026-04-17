// TEST: va_list_chain
// DESCRIPTION: va_list passed through multiple function levels with prefix params
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SQLite's printf chain crashes sqlite3_open in jmcc:
     MPrintf(db, "%s", str)        // variadic, builds va_list
       -> VMPrintf(db, fmt, ap)    // forwards va_list
            -> vappendf(acc, fmt, ap)  // consumes via va_arg

   Each level has 2-3 fixed parameters before the va_list. The fixed
   parameters BEFORE va_list shift where the variadic args land in
   registers (rdi, rsi consumed by named args; first va arg starts at rdx).

   When jmcc forwards va_list through multiple calls, va_arg() at the
   bottom reads garbage / NULL instead of the original argument.

   Test 157 (basic va_list) passes; this test exercises the chained
   forwarding pattern that SQLite uses. */

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

char captured[256];

/* Level 3: consumer */
void vappendf(void *acc, const char *fmt, va_list ap) {
    if (fmt[0] == '%' && fmt[1] == 's') {
        char *s = va_arg(ap, char *);
        if (s) {
            strcpy(captured, s);
        } else {
            strcpy(captured, "(null)");
        }
    }
}

/* Level 2: forwards va_list to consumer */
void VMPrintf(void *db, const char *zFormat, va_list ap) {
    char *acc = "dummy";
    vappendf(acc, zFormat, ap);
}

/* Level 1: variadic entry */
void MPrintf(void *db, const char *zFormat, ...) {
    va_list ap;
    va_start(ap, zFormat);
    VMPrintf(db, zFormat, ap);
    va_end(ap);
}

int main(void) {
    int db = 0;
    MPrintf(&db, "%s", "hello");
    if (strcmp(captured, "hello") != 0) return 1;

    /* Repeat with different args */
    MPrintf(&db, "%s", "world");
    if (strcmp(captured, "world") != 0) return 2;

    printf("ok\n");
    return 0;
}
