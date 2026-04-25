// TEST: typedef_opaque_struct_member_access
// DESCRIPTION: Darwin stdio.h defines FILE as a typedef to struct __sFILE.
//              Inline helper functions like __sputc access internal FILE fields
//              directly (e.g. f->_w, f->_lbfsize, f->_p).
//              jmcc must resolve typedef'd pointers to their underlying struct
//              type when performing member access (->), otherwise it emits
//              "member access requires a struct type" and corrupts parser state
//              for all subsequent declarations in the translation unit.
//              Regression test for Chocolate Doom / stdio.h __sputc on arm64.
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

/* Access FILE internal field via typedef pointer - mirrors __sputc in stdio.h */
inline int test_file_w(FILE *f) {
    return f->_w;
}

int main(void) {
    printf("OK\n");
    return 0;
}
