// TEST: struct_array_member_decay
// DESCRIPTION: struct_array[i].char_member must decay to pointer when passed to function
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's P_InitPicAnims does:
     R_TextureNumForName(animdefs[i].endname)
   where animdefs is an array of structs and endname is char[9].
   animdefs[i].endname must decay to char* (pointer to the char array).
   If it loads endname[0] (a char value) instead, the function gets
   a small integer as the "string pointer" and segfaults. */

int printf(const char *fmt, ...);
int strlen(const char *s);

typedef struct {
    int type;
    char endname[9];
    char startname[9];
    int speed;
} animdef_t;

animdef_t defs[] = {
    {1, "NUKAGE3", "NUKAGE1", 8},
    {0, "BLODGR4", "BLODGR1", 8},
};

int main(void) {
    /* defs[0].endname must decay to char* */
    int len = strlen(defs[0].endname);
    if (len != 7) return 1;  /* "NUKAGE3" = 7 chars */

    len = strlen(defs[1].startname);
    if (len != 7) return 2;

    /* With variable index */
    int i = 1;
    len = strlen(defs[i].endname);
    if (len != 7) return 3;

    /* Compare first char */
    if (defs[0].endname[0] != 'N') return 4;
    if (defs[1].startname[0] != 'B') return 5;

    printf("ok\n");
    return 0;
}
