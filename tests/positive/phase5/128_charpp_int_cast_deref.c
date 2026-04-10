// TEST: charpp_int_cast_deref
// DESCRIPTION: *(int*)charpp[i] must read 4 bytes from the string pointer, not from the array
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's R_InitSpriteDefs does:
     intname = *(int *)namelist[i];
   where namelist is char**. This reads 4 bytes from the string
   pointed to by namelist[i] as an integer (for fast name comparison).

   If namelist[i] returns the wrong pointer (e.g., the array base
   instead of the string address), the int cast reads garbage. */

int printf(const char *fmt, ...);

char *names[] = {"TROO", "SHTG", "PUNG", "PISG"};

int main(void) {
    /* The Doom pattern: cast string to int pointer and dereference */
    int intname = *(int *)names[0];
    /* "TROO" as little-endian int: 'T'=0x54, 'R'=0x52, 'O'=0x4F, 'O'=0x4F */
    /* = 0x4F4F5254 */
    if (intname != 0x4F4F5254) return 1;

    intname = *(int *)names[1];
    /* "SHTG" = 0x47544853 */
    if (intname != 0x47544853) return 2;

    /* Through a char** variable (like namelist parameter) */
    char **list = names;
    intname = *(int *)list[2];
    /* "PUNG" = 0x474E5550 */
    if (intname != 0x474E5550) return 3;

    /* With variable index */
    int i = 3;
    intname = *(int *)list[i];
    /* "PISG" = 0x47534950 */
    if (intname != 0x47534950) return 4;

    printf("ok\n");
    return 0;
}
