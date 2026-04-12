// TEST: variadic_va_list_abi
// DESCRIPTION: Variadic functions must implement AMD64 va_list ABI correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's I_Error is: void I_Error(char *error, ...)
   It uses va_start/vfprintf to format the error message.
   On AMD64, va_list is a struct:
     { uint32 gp_offset, uint32 fp_offset,
       void *overflow_arg_area, void *reg_save_area }
   If gp_offset/fp_offset are missing or the layout is wrong,
   vfprintf reads garbage and crashes (SIGSEGV in strlen).
   This caused Doom's menu Escape crash: S_StartSound triggers
   I_Error("Bad sfx #: %d", id) with broken va_list. */

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

/* Variadic function that formats into a buffer using va_list */
int my_sprintf(char *buf, const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    int ret = vsprintf(buf, fmt, ap);
    va_end(ap);
    return ret;
}

/* Test with multiple argument types */
int my_snprintf(char *buf, int size, const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    int ret = vsnprintf(buf, size, fmt, ap);
    va_end(ap);
    return ret;
}

int printf(const char *fmt, ...);

int main(void) {
    char buf[256];

    /* Test 1: single int arg */
    my_sprintf(buf, "val=%d", 42);
    if (strcmp(buf, "val=42") != 0) return 1;

    /* Test 2: single string arg (crashes if va_list wrong: strlen on garbage ptr) */
    my_sprintf(buf, "name=%s", "hello");
    if (strcmp(buf, "name=hello") != 0) return 2;

    /* Test 3: multiple args (int, string, int) */
    my_sprintf(buf, "%d-%s-%d", 10, "mid", 20);
    if (strcmp(buf, "10-mid-20") != 0) return 3;

    /* Test 4: 5 variadic args (all in registers on AMD64) */
    my_sprintf(buf, "%d %d %d %d %d", 1, 2, 3, 4, 5);
    if (strcmp(buf, "1 2 3 4 5") != 0) return 4;

    /* Test 5: 7+ args (some on stack) */
    my_snprintf(buf, 256, "%d %d %d %d %d %d %d", 1, 2, 3, 4, 5, 6, 7);
    if (strcmp(buf, "1 2 3 4 5 6 7") != 0) return 5;

    /* Test 6: Doom's exact I_Error pattern */
    my_sprintf(buf, "Bad sfx #: %d", 23);
    if (strcmp(buf, "Bad sfx #: 23") != 0) return 6;

    printf("ok\n");
    return 0;
}
