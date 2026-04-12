// TEST: func_ptr_array_decl
// DESCRIPTION: Array of function pointers with unsized [] in declarator must parse
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Chocolate Doom's p_acs.c declares:
     static int (*PCodeCmds[])(void) = { func1, func2, ... };
   This is an array of function pointers with implicit size.
   jmcc fails to parse [] inside the function pointer declarator. */

int printf(const char *fmt, ...);

int cmd_a(void) { return 1; }
int cmd_b(void) { return 2; }
int cmd_c(void) { return 3; }

/* Array of function pointers — unsized */
static int (*commands[])(void) = {
    cmd_a,
    cmd_b,
    cmd_c
};

/* With explicit size */
static int (*commands2[3])(void) = {
    cmd_a,
    cmd_b,
    cmd_c
};

#define NUM_COMMANDS (sizeof(commands)/sizeof(commands[0]))

int main(void) {
    if (NUM_COMMANDS != 3) return 1;
    if (commands[0]() != 1) return 2;
    if (commands[1]() != 2) return 3;
    if (commands[2]() != 3) return 4;
    if (commands2[0]() != 1) return 5;

    /* Call through index */
    int total = 0;
    int i;
    for (i = 0; i < 3; i++)
        total += commands[i]();
    if (total != 6) return 6;

    printf("ok\n");
    return 0;
}
