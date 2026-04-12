// TEST: 2d_char_array_string_init
// DESCRIPTION: 2D char array initialized with string literals must contain the strings
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's m_menu.c has:
     char skullName[2][9] = {"M_SKULL1","M_SKULL2"};
   jmcc emits all zeros instead of the string data, so
   W_CacheLumpName(skullName[whichSkull], PU_CACHE) fails
   because the name is empty. This crashes the menu. */

int printf(const char *fmt, ...);
int strcmp(const char *a, const char *b);

/* Exact Doom pattern */
char skullName[2][9] = {"M_SKULL1", "M_SKULL2"};

/* Simpler case */
char names[3][4] = {"abc", "def", "ghi"};

/* Partial init */
char partial[2][6] = {"hi"};

int main(void) {
    /* Test 1: Doom's exact pattern */
    if (skullName[0][0] != 'M') return 1;
    if (strcmp(skullName[0], "M_SKULL1") != 0) return 2;
    if (strcmp(skullName[1], "M_SKULL2") != 0) return 3;

    /* Test 2: simpler 2D char array with strings */
    if (strcmp(names[0], "abc") != 0) return 4;
    if (strcmp(names[1], "def") != 0) return 5;
    if (strcmp(names[2], "ghi") != 0) return 6;

    /* Test 3: individual char access */
    if (names[1][1] != 'e') return 7;
    if (skullName[1][2] != 'S') return 8;

    /* Test 4: partial init - first row has string, second should be zeros */
    if (strcmp(partial[0], "hi") != 0) return 9;
    if (partial[1][0] != 0) return 10;

    printf("ok\n");
    return 0;
}
