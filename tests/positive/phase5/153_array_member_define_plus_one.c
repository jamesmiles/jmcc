// TEST: array_member_define_plus_one
// DESCRIPTION: Array member sized with DEFINE+1 must evaluate to correct size
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's hu_textline_t has char l[HU_MAXLINELENGTH+1] where
   HU_MAXLINELENGTH is #define 80. The array should be 81 bytes.
   jmcc evaluates the size as 1 instead of 81, making sizeof
   hu_textline_t = 32 instead of 112. This corrupts all widget
   structs that embed hu_textline_t. */

int printf(const char *fmt, ...);

#define MAXLEN 80

typedef struct {
    int x;
    int y;
    void *f;
    int sc;
    char l[MAXLEN+1];
    int len;
    int update;
} textline_t;

int main(void) {
    if (sizeof(textline_t) != 112) {
        printf("FAIL: sizeof=%lu expected 112\n", (unsigned long)sizeof(textline_t));
        return 1;
    }

    /* Check offset of len (should be after 81-byte array) */
    textline_t t;
    t.len = 42;
    t.l[80] = 'Z';  /* last valid index */
    if (t.l[80] != 'Z') return 2;
    if (t.len != 42) return 3;  /* corruption if array too small */

    printf("ok\n");
    return 0;
}
