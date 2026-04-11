// TEST: ptr_array_null_terminator
// DESCRIPTION: char* array with 0/NULL terminator must emit .quad 0 for the NULL entry
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's sprnames[] is a char*[] terminated with 0 (NULL).
   R_InitSpriteDefs iterates while(*check != NULL) to count entries.
   If the compiler doesn't emit .quad 0 for the NULL/0 entry,
   the loop reads past the array into subsequent data, crashing. */

int printf(const char *fmt, ...);

char *names[] = {"hello", "world", 0};
int sentinel = 42;

int main(void) {
    /* Count entries using NULL-terminated iteration */
    int count = 0;
    char **p = names;
    while (*p != 0) {
        count++;
        p++;
    }
    if (count != 2) return 1;  /* should find 2 entries */

    /* Verify sentinel wasn't corrupted */
    if (sentinel != 42) return 2;

    /* Verify the NULL is at index 2 */
    if (names[2] != 0) return 3;

    printf("ok\n");
    return 0;
}
