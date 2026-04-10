// TEST: charpp_double_index
// DESCRIPTION: Double indexing char** (argv[i][j]) must dereference correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom parses command line arguments with patterns like:
     startepisode = myargv[p+1][0] - '0';
   myargv is char**, so myargv[p+1] is char*, and [0] gets the first
   character. If the second indexing step uses the wrong stride or
   the intermediate pointer is truncated, it reads the wrong byte.

   This causes -warp 1 1 to parse as episode=-2 map=0 instead of 1 1. */

int printf(const char *fmt, ...);

char *strings[] = {"hello", "world", "test", "doom"};
char **argv_like = strings;

int main(void) {
    /* Direct double-index on char** */
    if (strings[0][0] != 'h') return 1;
    if (strings[0][1] != 'e') return 2;
    if (strings[1][0] != 'w') return 3;
    if (strings[2][0] != 't') return 4;
    if (strings[3][3] != 'm') return 5;

    /* Through a char** variable */
    char **pp = strings;
    if (pp[0][0] != 'h') return 6;
    if (pp[1][0] != 'w') return 7;
    if (pp[2][0] != 't') return 8;

    /* The Doom pattern: variable index + [0] */
    int i = 1;
    if (pp[i][0] != 'w') return 9;
    i = 2;
    if (pp[i][0] != 't') return 10;

    /* Arithmetic on the char value */
    char c = pp[0][0];
    int val = c - 'a';
    if (val != 7) return 11;  /* 'h' - 'a' = 7 */

    /* pp[i+1][0] pattern */
    i = 0;
    if (pp[i+1][0] != 'w') return 12;

    printf("ok\n");
    return 0;
}
