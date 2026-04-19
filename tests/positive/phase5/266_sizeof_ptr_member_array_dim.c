// TEST: sizeof_ptr_member_array_dim
// DESCRIPTION: sizeof(ptr->arr_field) used as array declarator dimension must give correct size, not always 4
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
#include <stdio.h>
#include <string.h>

struct Pager {
    char unused;
    char dbFileVers[16];   /* 16-byte version tag — SQLite uses this pattern */
    int x;
};

int main(void) {
    int ok = 1;
    struct Pager pager;
    struct Pager *p = &pager;

    /* sizeof(p->dbFileVers) must be 16 */
    if ((int)sizeof(p->dbFileVers) != 16) {
        printf("FAIL: sizeof(p->dbFileVers)=%d expected 16\n", (int)sizeof(p->dbFileVers));
        ok = 0;
    }

    /* char buf[sizeof(p->dbFileVers)] must have sizeof(buf) == 16 */
    char buf[sizeof(p->dbFileVers)];
    if ((int)sizeof(buf) != 16) {
        printf("FAIL: sizeof(char buf[sizeof(p->dbFileVers)])=%d expected 16\n", (int)sizeof(buf));
        ok = 0;
    }

    /* memset/memcpy using sizeof as dimension must touch all 16 bytes */
    memset(p->dbFileVers, 0xAA, sizeof(p->dbFileVers));
    memset(buf, 0, sizeof(buf));
    memcpy(buf, p->dbFileVers, sizeof(buf));

    int n_copied = 0;
    for (int i = 0; i < 16; i++) if ((unsigned char)buf[i] == 0xAA) n_copied++;
    if (n_copied != 16) {
        printf("FAIL: only %d/16 bytes set via sizeof-based memcpy\n", n_copied);
        ok = 0;
    }

    /* Test with other field types */
    struct S2 { char arr4[4]; char arr8[8]; char arr32[32]; };
    struct S2 *q;
    char b4[sizeof(q->arr4)];
    char b8[sizeof(q->arr8)];
    char b32[sizeof(q->arr32)];
    if ((int)sizeof(b4) != 4)  { printf("FAIL: arr4 dim=%d\n", (int)sizeof(b4)); ok = 0; }
    if ((int)sizeof(b8) != 8)  { printf("FAIL: arr8 dim=%d\n", (int)sizeof(b8)); ok = 0; }
    if ((int)sizeof(b32) != 32){ printf("FAIL: arr32 dim=%d\n", (int)sizeof(b32)); ok = 0; }

    if (ok) printf("ok\n");
    return ok ? 0 : 1;
}
