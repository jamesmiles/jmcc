// TEST: u8_struct_member_deref
// DESCRIPTION: Indexing a u8* obtained via struct->member must zero-extend, not sign-extend
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SQLite's findCell() macro reads cell offsets from a B-tree page header:
     #define findCell(P,I) \
       ((P)->aData + ((P)->maskPage & get2byteAligned(&(P)->aCellIdx[2*(I)])))
     #define get2byteAligned(x)  ((x)[0]<<8 | (x)[1])

   where aCellIdx is `u8 *aCellIdx` (unsigned char pointer). If the low byte
   has its high bit set (e.g. 0xb3), the expression `(x[0] << 8) | x[1]` should
   yield a positive value: (0x0f << 8) | 0xb3 = 0x0fb3.

   jmcc emits `movsbl` (sign-extend) instead of `movzbl` when dereferencing a
   u8* field accessed through a struct pointer, so x[1] = 0xb3 becomes
   0xffffffb3 (signed-extended). OR'd with 0x0f00 gives 0xffffffb3, truncated
   to u16 as 0xffb3 instead of 0x0fb3.

   This corrupts SQLite's B-tree cell lookup, causing "database disk image
   is malformed" errors on CREATE INDEX when any referenced table has a FOREIGN
   KEY (because the FK machinery exercises sqlite_master reads that hit cells
   whose offset bytes happen to have the high bit set).

   The bug manifests only when:
     1. The u8* is reached via struct->member (not struct.member or local var)
     2. The byte being read has its high bit set (>= 0x80) */

#include <stdio.h>

typedef unsigned char u8;
typedef unsigned short u16;

typedef struct Page {
    u8 *aData;
    u8 *aCellIdx;
    u16 maskPage;
} Page;

static u8 buffer[64];

int main(void) {
    Page pg;
    pg.aData = buffer;
    pg.aCellIdx = buffer + 8;
    pg.maskPage = 0xffff;

    pg.aCellIdx[0] = 0x0f;
    pg.aCellIdx[1] = 0xb3;
    pg.aCellIdx[2] = 0x0e;
    pg.aCellIdx[3] = 0xff;

    Page *p = &pg;

    /* Direct array access (works in jmcc today): */
    u8 *arr = p->aCellIdx;
    u16 v0 = (arr[0] << 8) | arr[1];
    if (v0 != 0x0fb3) { printf("FAIL direct: got 0x%x want 0xfb3\n", v0); return 1; }

    /* Through struct arrow (buggy in jmcc): */
    u16 v1 = (p->aCellIdx[0] << 8) | p->aCellIdx[1];
    if (v1 != 0x0fb3) { printf("FAIL arrow0: got 0x%x want 0xfb3\n", v1); return 2; }

    u16 v2 = (p->aCellIdx[2] << 8) | p->aCellIdx[3];
    if (v2 != 0x0eff) { printf("FAIL arrow2: got 0x%x want 0xeff\n", v2); return 3; }

    /* Expression with index computation like SQLite's 2*i */
    int i = 0;
    u16 v3 = (p->aCellIdx[2*i] << 8) | p->aCellIdx[2*i+1];
    if (v3 != 0x0fb3) { printf("FAIL arrow_idx: got 0x%x want 0xfb3\n", v3); return 4; }

    /* SQLite's exact macro form: take address of &p->aCellIdx[2*i], then [0]/[1] */
#define get2ba(x)  ((x)[0]<<8 | (x)[1])
    for (int k = 0; k < 2; k++) {
        u16 vk = get2ba(&p->aCellIdx[2*k]);
        u16 want = k==0 ? 0x0fb3 : 0x0eff;
        if (vk != want) { printf("FAIL macro k=%d: got 0x%x want 0x%x\n", k, vk, want); return 5 + k; }
    }

    printf("ok\n");
    return 0;
}
