/* Regression: switch case labels that are compile-time constant expressions
 * (not just integer literals) must be accepted by jmcc on arm64-apple-darwin.
 *
 * Mirrors st_stuff.c which uses:
 *   case ((('a'<<24)+('m'<<16)) | ('e'<<8)):
 *   case ((('a'<<24)+('m'<<16)) | ('x'<<8)):
 * These are ICEs (integer constant expressions) — valid C99 case labels.
 */

int decode_cmd(int x) {
    switch (x) {
        case (('a'<<24)+('m'<<16)):          return 1;
        case (('a'<<24)+('m'<<16))|('e'<<8): return 2;
        case (('a'<<24)+('m'<<16))|('x'<<8): return 3;
        case (1<<8)|(2<<4)|3:                return 4;
        default:                              return 0;
    }
}

int main(void) {
    return decode_cmd(0);
}
