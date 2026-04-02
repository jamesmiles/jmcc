// TEST: char_literal_paren
// DESCRIPTION: '(' char literal must not trigger multi-line macro arg joining
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: (
// STDOUT: )
// STDOUT: done
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

/* Doom's hu_stuff.c has a char lookup table with:
       '(', // shift-9
   The '(' char literal triggers the paren counter in the multi-line
   macro joiner, collapsing subsequent lines. */

char shiftxform[] = {
    ' ', '!', '"', '#', '$', '%', '&',
    '(', // shift-9
    ')', '*', '+', '<',
    '-', '>', '?', '@'
};

int main(void) {
    printf("%c\n", shiftxform[7]);
    printf("%c\n", shiftxform[8]);
    printf("done\n");
    return 0;
}
