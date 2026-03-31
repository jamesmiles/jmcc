// TEST: struct_array_member
// DESCRIPTION: Struct with array member accessed through pointer
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: vals[3]=42
// STDOUT: vals[7]=99
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

typedef struct {
    int type;
    int vals[8];
} sector_t;

void fill(sector_t *s) {
    s->vals[3] = 42;
    s->vals[7] = 99;
}

int main(void) {
    sector_t sec;
    sec.type = 1;
    fill(&sec);
    printf("vals[3]=%d\n", sec.vals[3]);
    printf("vals[7]=%d\n", sec.vals[7]);
    return 0;
}
