// TEST: for_loop_declaration
// DESCRIPTION: Variable declarations in for-loop init must work correctly
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* C99 allows variable declarations in for-loop initializers:
     for (int i = 0; i < n; i++)
   Chocolate Doom uses this in i_main.c. The variable must be
   scoped to the loop body and must not leak into the enclosing scope. */

int printf(const char *fmt, ...);

int main(void) {
    int total;

    /* Test 1: basic for-loop declaration */
    total = 0;
    for (int i = 0; i < 5; i++)
        total += i;
    if (total != 10) return 1;

    /* Test 2: loop var doesn't leak into outer scope */
    /* (if 'i' leaked, this redeclaration would conflict) */
    for (int i = 10; i < 13; i++)
        total += i;
    if (total != 10 + 10 + 11 + 12) return 2;

    /* Test 3: nested for-loop declarations */
    total = 0;
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++)
            total += i * 3 + j;
    /* 0+1+2+3+4+5+6+7+8 = 36 */
    if (total != 36) return 3;

    /* Test 4: same variable name in sequential loops */
    total = 0;
    for (int x = 0; x < 4; x++)
        total += x;
    for (int x = 10; x < 14; x++)
        total += x;
    /* (0+1+2+3) + (10+11+12+13) = 6 + 46 = 52 */
    if (total != 52) return 4;

    /* Test 5: declaration with pointer type */
    int arr[] = {10, 20, 30, 40, 50};
    total = 0;
    for (int *p = arr; p < arr + 5; p++)
        total += *p;
    if (total != 150) return 5;

    /* Test 6: declaration with unsigned type */
    total = 0;
    for (unsigned int i = 0; i < 3; i++)
        total += i;
    if (total != 3) return 6;

    /* Test 7: multiple variables in init (C99 allows this) */
    total = 0;
    for (int i = 0, j = 10; i < 3; i++, j--)
        total += i + j;
    /* (0+10)+(1+9)+(2+8) = 10+10+10 = 30 */
    if (total != 30) return 7;

    /* Test 8: loop with no body iterations (immediate exit) */
    total = 0;
    for (int i = 0; i < 0; i++)
        total = 999;
    if (total != 0) return 8;

    /* Test 9: complex expression in condition using loop var */
    total = 0;
    for (int i = 1; i * i <= 25; i++)
        total += i;
    /* 1+2+3+4+5 = 15 */
    if (total != 15) return 9;

    /* Test 10: loop variable used in array index */
    int results[5];
    for (int i = 0; i < 5; i++)
        results[i] = i * i;
    if (results[4] != 16) return 10;

    printf("ok\n");
    return 0;
}
