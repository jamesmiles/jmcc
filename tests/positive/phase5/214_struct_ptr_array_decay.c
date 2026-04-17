// TEST: struct_ptr_array_decay
// DESCRIPTION: void* array member of struct must decay to void** when used as rvalue
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* SQLite's WhereLoop struct has:
     WhereTerm *aLTermSpace[3];   // void* array member
     WhereTerm **aLTerm;          // pointer
   And does:
     p->aLTerm = p->aLTermSpace;  // ptr-to-array decay
     p->aLTerm[0] = pTerm;        // dereference

   jmcc dereferences `p->aLTermSpace` instead of decaying it to a pointer,
   so aLTerm gets the value of aLTermSpace[0] (some uninitialized stack
   value). Subsequent writes through aLTerm crash.

   This blocks SQLite's whereShortCut from setting up the query plan,
   crashing CREATE TABLE.

   Earlier tests covered:
     int arr[] in struct (works in jmcc)
     pointer-to-array in cast contexts (test 178)
   This is specifically: void* arr[] member used as rvalue. */

int printf(const char *fmt, ...);

struct WL {
    void **aLTerm;
    void *aLTermSpace[3];
};

int main(void) {
    struct WL p;

    /* Decay: array member used as rvalue should give address, not first element */
    p.aLTerm = p.aLTermSpace;

    /* These two should be equal */
    if (p.aLTerm != (void **)p.aLTermSpace) return 1;
    if ((void *)p.aLTerm != (void *)&p.aLTermSpace) return 2;

    /* Now writes through aLTerm should land in aLTermSpace */
    p.aLTerm[0] = (void *)0x100;
    p.aLTerm[1] = (void *)0x200;
    p.aLTerm[2] = (void *)0x300;

    if (p.aLTermSpace[0] != (void *)0x100) return 3;
    if (p.aLTermSpace[1] != (void *)0x200) return 4;
    if (p.aLTermSpace[2] != (void *)0x300) return 5;

    printf("ok\n");
    return 0;
}
