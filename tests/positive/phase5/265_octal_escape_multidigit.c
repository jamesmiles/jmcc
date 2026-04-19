// TEST: octal_escape_multidigit
// DESCRIPTION: string literal octal escape \NNN must consume all 3 octal digits, not just \N
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
#include <string.h>

int main(void) {
    int ok = 1;

    /* "\000" = one NUL byte (octal 000 = 0), NOT '\0'+'0'+'0' */
    /* Length should be 1 (just the NUL, which terminates the string) */
    /* But the array itself has length 1 */
    const char a[] = "X\000Y";  /* should be {'X','\0','Y','\0'}, length 4 */
    if (a[0] != 'X') { printf("FAIL a[0]='%c'\n", a[0]); ok = 0; }
    if (a[1] != '\0') { printf("FAIL a[1]=0x%02x not NUL\n", (unsigned char)a[1]); ok = 0; }
    if (a[2] != 'Y') { printf("FAIL a[2]='%c' expected 'Y'\n", a[2]); ok = 0; }
    if (a[3] != '\0') { printf("FAIL a[3]=0x%02x not NUL\n", (unsigned char)a[3]); ok = 0; }

    /* "\012" = one byte with value 10 (octal 012 = 10 decimal) */
    const char b[] = "\012";  /* should be {'\n', '\0'} */
    if (b[0] != '\n') { printf("FAIL b[0]=0x%02x expected 0x0a\n", (unsigned char)b[0]); ok = 0; }
    if (b[1] != '\0') { printf("FAIL b[1]=0x%02x not NUL\n", (unsigned char)b[1]); ok = 0; }

    /* "\101" = 65 = 'A' in octal */
    const char c[] = "\101";  /* should be {'A', '\0'} */
    if (c[0] != 'A') { printf("FAIL c[0]='%c' expected 'A'\n", c[0]); ok = 0; }
    if (c[1] != '\0') { printf("FAIL c[1]=0x%02x not NUL\n", (unsigned char)c[1]); ok = 0; }

    /* The actual pattern from SQLite: "B\000C\000D\000E\000F" */
    /* Should be: B=0x42, \0, C=0x43, \0, D=0x44, \0, E=0x45, \0, F=0x46 */
    static const char zAff[] = "B\000C\000D\000E\000F";
    if (zAff[0] != 'B') { printf("FAIL zAff[0]='%c'\n", zAff[0]); ok = 0; }
    if (zAff[1] != '\0') { printf("FAIL zAff[1]=0x%02x not NUL\n", (unsigned char)zAff[1]); ok = 0; }
    if (zAff[2] != 'C') { printf("FAIL zAff[2]='%c' expected 'C'\n", zAff[2]); ok = 0; }
    if (zAff[4] != 'D') { printf("FAIL zAff[4]='%c' expected 'D'\n", zAff[4]); ok = 0; }
    if (zAff[6] != 'E') { printf("FAIL zAff[6]='%c' expected 'E'\n", zAff[6]); ok = 0; }

    if (ok) printf("ok\n");
    return ok ? 0 : 1;
}
