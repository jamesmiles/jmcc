// TEST: 2d_array_row_init
// DESCRIPTION: 2D array row used as pointer initializer must decay to address
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's st_stuff.c has:
     unsigned char cheat_powerup_seq[7][10] = {...};
     cheatseq_t cheat_powerup[7] = {
         { cheat_powerup_seq[0], 0 },
         { cheat_powerup_seq[1], 0 },
         ...
     };
   cheat_powerup_seq[i] should decay to unsigned char* (pointer to
   row i). But jmcc emits NULL instead of the row address. */

int printf(const char *fmt, ...);

unsigned char table[3][4] = {
    {10, 20, 30, 40},
    {50, 60, 70, 80},
    {90, 100, 110, 120}
};

typedef struct {
    unsigned char *seq;
    unsigned char *p;
} entry_t;

entry_t entries[3] = {
    { table[0], 0 },
    { table[1], 0 },
    { table[2], 0 }
};

int main(void) {
    if (entries[0].seq == 0) return 1;  /* NULL = not initialized */
    if (entries[0].seq[0] != 10) return 2;
    if (entries[1].seq[0] != 50) return 3;
    if (entries[2].seq[3] != 120) return 4;

    printf("ok\n");
    return 0;
}
