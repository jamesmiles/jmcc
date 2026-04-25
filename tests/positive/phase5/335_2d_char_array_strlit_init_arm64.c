/* Regression: global 2D char array (char[][N]) initialized with braced
 * string literals — { {"str1"}, {"str2"} } — fails with:
 *   "does not yet support this global initializer value"
 *
 * This pattern appears in Chocolate Doom:
 *   hexen/sb_bar.c: char patcharti[][10] = { {"ARTIBOX"}, {"ARTIINVU"}, ... }
 *   heretic/sb_bar.c: char patcharti[][10] = { {"ARTIBOX"}, ... }
 *   doom/st_stuff.c: similar patterns
 *
 * clang accepts this; jmcc must do the same.
 */

char names[][10] = {
    {"ARTIBOX"},
    {"ARTIINVU"},
    {"ARTIPTN2"},
    {""}
};

int main(void) {
    /* "ARTIBOX": A=65, R=82, T=84, I=73, B=66, O=79, X=88 */
    return (names[0][0] == 'A' && names[1][0] == 'A' && names[2][0] == 'A') ? 0 : 1;
}
