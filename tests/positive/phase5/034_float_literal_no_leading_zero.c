// TEST: float_literal_no_leading_zero
// DESCRIPTION: Float literal without leading zero like .867 (Doom's am_map chevron coords)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: -56819
// STDOUT: -32768
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

int main(void) {
    /* Doom's am_map.c uses .867 and -.867 in initializer lists */
    double a = .867;
    double b = -.5;
    int fa = (int)(a * ((1 << 16)));   /* .867 * 65536 = ~56834 */
    int fb = (int)(b * ((1 << 16)));   /* -.5 * 65536 = -32768 */

    /* Doom's actual pattern: fixed-point chevron coordinates */
    int chevron_x = (int)(-.867 * ((1 << 16)));
    int chevron_y = (int)(-.5 * ((1 << 16)));
    printf("%d\n", chevron_x);
    printf("%d\n", chevron_y);
    return 0;
}
