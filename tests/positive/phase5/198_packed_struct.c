// TEST: packed_struct
// DESCRIPTION: __attribute__((packed)) must remove struct padding
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Chocolate Doom's midifile.c defines packed structs for MIDI file
   headers (no padding between fields since file format is fixed):
     typedef struct {
         byte chunk_id[4];
         unsigned int chunk_size;
     } __attribute__((packed, gcc_struct)) chunk_header_t;
   Expected size: 8. jmcc currently ignores the packed attribute
   and adds natural alignment padding, making the struct 16 bytes
   instead of 14 for midi_header_t. fread() then consumes too many
   bytes, shifting all subsequent reads by 2 — "MTrk" becomes "??rk"
   and Chocolate Doom fails to parse MIDI tracks.

   jmcc must honor __attribute__((packed)) to make this work. */

int printf(const char *fmt, ...);

typedef unsigned char byte;

/* Padding would normally put 3 bytes after 'a' to align the int */
typedef struct {
    byte a;
    unsigned int b;
} __attribute__((packed)) packed1_t;

/* Without packed: 8 bytes. With packed: 5 bytes. */

/* Nested packed: MIDI header pattern */
typedef struct {
    byte id[4];
    unsigned int size;
} __attribute__((packed)) chunk_t;

typedef struct {
    chunk_t chunk;
    unsigned short format;
    unsigned short tracks;
    unsigned short division;
} __attribute__((packed)) midi_hdr_t;

/* Without packed: 16 bytes (chunk=8 + 6 shorts + 2 padding).
   With packed: 14 bytes (chunk=8 + 3*2). */

int main(void) {
    /* Test 1: basic packed struct */
    if (sizeof(packed1_t) != 5) return 1;

    /* Test 2: nested packed struct (MIDI header pattern) */
    if (sizeof(chunk_t) != 8) return 2;
    if (sizeof(midi_hdr_t) != 14) return 3;

    /* Test 3: offset of chunk_size */
    packed1_t p;
    unsigned char *base = (unsigned char *)&p;
    unsigned char *b_ptr = (unsigned char *)&p.b;
    if ((b_ptr - base) != 1) return 4;

    /* Test 4: field access still works */
    p.a = 0x12;
    p.b = 0x78563412;
    if (p.a != 0x12) return 5;
    if (p.b != 0x78563412) return 6;

    printf("ok\n");
    return 0;
}
