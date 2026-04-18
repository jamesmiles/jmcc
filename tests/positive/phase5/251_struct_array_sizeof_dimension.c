// TEST: struct_array_sizeof_dimension
// DESCRIPTION: struct member array dimension computed via sizeof must yield correct struct size
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* sqlite3.c Bitvec struct (line ~53480):
     typedef struct Bitvec Bitvec;
     #define BITVEC_USIZE (((512-(3*sizeof(u32)))/sizeof(Bitvec*))*sizeof(Bitvec*))
     #define BITVEC_NPTR  (BITVEC_USIZE/sizeof(Bitvec *))
     struct Bitvec { u32 a,b,c; union { ...; Bitvec *apSub[BITVEC_NPTR]; } u; };
     assert(sizeof(*p) == 512);
   Bug: when an array dimension inside a struct member is a macro expression
   containing sizeof(), jmcc treats the array as having 1 element (element-size
   bytes) instead of N elements.  sizeof(Bitvec) evaluates to 24 instead of 512,
   causing sqlite3BitvecCreate to call malloc(24) and every subsequent bitmap
   write to overflow into the heap. */

#include <stdio.h>

typedef struct T T;
struct T { int x; };

/* N = 62 when sizeof(T*) = 8; jmcc must not reduce to 1 */
#define N (496 / sizeof(T*))

struct S { T *arr[N]; };  /* correct size: 62 * 8 = 496 bytes */

int main(void) {
    if (sizeof(struct S) != (size_t)N * sizeof(T*)) {
        printf("FAIL: sizeof(S) = %zu, expected %zu (N=%zu, sizeof(T*)=%zu)\n",
               sizeof(struct S), (size_t)N * sizeof(T*), (size_t)N, sizeof(T*));
        return 1;
    }
    printf("ok\n");
    return 0;
}
