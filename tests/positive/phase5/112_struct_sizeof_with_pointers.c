// TEST: struct_sizeof_with_pointers
// DESCRIPTION: sizeof struct with mixed int and pointer fields must account for padding
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's memblock_t has:
     int size; void** user; int tag; int id;
     struct memblock_s *next; struct memblock_s *prev;
   On 64-bit: 4 + 4(pad) + 8 + 4 + 4 + 8 + 8 = 40 bytes.
   If sizeof computes wrong, pointer arithmetic like
     (byte*)base + sizeof(memblock_t)
   lands at the wrong address, corrupting zone block headers. */

int printf(const char *fmt, ...);

struct memblock {
    int size;
    void **user;
    int tag;
    int id;
    struct memblock *next;
    struct memblock *prev;
};

struct simple {
    int a;
    void *p;
};

struct packed_ints {
    int a;
    int b;
    int c;
};

int main(void) {
    /* memblock_t: int(4) + pad(4) + ptr(8) + int(4) + int(4) + ptr(8) + ptr(8) = 40 */
    if (sizeof(struct memblock) != 40) return 1;

    /* simple: int(4) + pad(4) + ptr(8) = 16 */
    if (sizeof(struct simple) != 16) return 2;

    /* packed_ints: 3 * int(4) = 12 */
    if (sizeof(struct packed_ints) != 12) return 3;

    /* Pointer arithmetic using sizeof */
    char buf[100];
    struct memblock *b1 = (struct memblock *)buf;
    struct memblock *b2 = (struct memblock *)(buf + sizeof(struct memblock));

    long diff = (char *)b2 - (char *)b1;
    if (diff != 40) return 4;

    /* The actual Doom pattern: (byte *)base + size where size was computed
       using sizeof(memblock_t) */
    int block_size = sizeof(struct memblock) + 64;  /* header + payload */
    char *payload = (char *)b1 + sizeof(struct memblock);
    long payload_off = payload - buf;
    if (payload_off != 40) return 5;

    printf("ok\n");
    return 0;
}
