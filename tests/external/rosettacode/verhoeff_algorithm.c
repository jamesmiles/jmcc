// TEST: rosetta_verhoeff_algorithm
// DESCRIPTION: Rosetta Code - Verhoeff algorithm (UTF-8 subscript chars in string literal fail to parse)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Verhoeff_algorithm#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: Check digit calculations for '236':
// STDOUT:
// STDOUT:  i  nᵢ  p[i,nᵢ]  c
// STDOUT: ------------------
// STDOUT:  0  0      0     0
// STDOUT:  1  6      3     3
// STDOUT:  2  3      3     1
// STDOUT:  3  2      1     2
// STDOUT:
// STDOUT: inv[2] = 3
// STDOUT:
// STDOUT: The check digit for '236' is '3'.
// STDOUT: Validation calculations for '2363':
// STDOUT:
// STDOUT:  i  nᵢ  p[i,nᵢ]  c
// STDOUT: ------------------
// STDOUT:  0  3      3     3
// STDOUT:  1  6      3     1
// STDOUT:  2  3      3     4
// STDOUT:  3  2      1     0
// STDOUT:
// STDOUT: The validation for '2363' is correct.
// STDOUT: Validation calculations for '2369':
// STDOUT:
// STDOUT:  i  nᵢ  p[i,nᵢ]  c
// STDOUT: ------------------
// STDOUT:  0  9      9     9
// STDOUT:  1  6      3     6
// STDOUT:  2  3      3     8
// STDOUT:  3  2      1     7
// STDOUT:
// STDOUT: The validation for '2369' is incorrect.
// STDOUT: Check digit calculations for '12345':
// STDOUT:
// STDOUT:  i  nᵢ  p[i,nᵢ]  c
// STDOUT: ------------------
// STDOUT:  0  0      0     0
// STDOUT:  1  5      8     8
// STDOUT:  2  4      7     1
// STDOUT:  3  3      6     7
// STDOUT:  4  2      5     2
// STDOUT:  5  1      2     4
// STDOUT:
// STDOUT: inv[4] = 1
// STDOUT:
// STDOUT: The check digit for '12345' is '1'.
// STDOUT: Validation calculations for '123451':
// STDOUT:
// STDOUT:  i  nᵢ  p[i,nᵢ]  c
// STDOUT: ------------------
// STDOUT:  0  1      1     1
// STDOUT:  1  5      8     9
// STDOUT:  2  4      7     2
// STDOUT:  3  3      6     8
// STDOUT:  4  2      5     3
// STDOUT:  5  1      2     0
// STDOUT:
// STDOUT: The validation for '123451' is correct.
// STDOUT: Validation calculations for '123459':
// STDOUT:
// STDOUT:  i  nᵢ  p[i,nᵢ]  c
// STDOUT: ------------------
// STDOUT:  0  9      9     9
// STDOUT:  1  5      8     1
// STDOUT:  2  4      7     8
// STDOUT:  3  3      6     2
// STDOUT:  4  2      5     7
// STDOUT:  5  1      2     5
// STDOUT:
// STDOUT: The validation for '123459' is incorrect.
// STDOUT:
// STDOUT: The check digit for '123456789012' is '0'.
// STDOUT:
// STDOUT: The validation for '1234567890120' is correct.
// STDOUT:
// STDOUT: The validation for '1234567890129' is incorrect.

#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

static const int d[][10] = {
    {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, {1, 2, 3, 4, 0, 6, 7, 8, 9, 5},
    {2, 3, 4, 0, 1, 7, 8, 9, 5, 6}, {3, 4, 0, 1, 2, 8, 9, 5, 6, 7},
    {4, 0, 1, 2, 3, 9, 5, 6, 7, 8}, {5, 9, 8, 7, 6, 0, 4, 3, 2, 1},
    {6, 5, 9, 8, 7, 1, 0, 4, 3, 2}, {7, 6, 5, 9, 8, 2, 1, 0, 4, 3},
    {8, 7, 6, 5, 9, 3, 2, 1, 0, 4}, {9, 8, 7, 6, 5, 4, 3, 2, 1, 0},
};

static const int inv[] = {0, 4, 3, 2, 1, 5, 6, 7, 8, 9};

static const int p[][10] = {
    {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, {1, 5, 7, 6, 2, 8, 3, 0, 9, 4},
    {5, 8, 0, 3, 7, 9, 6, 1, 4, 2}, {8, 9, 1, 6, 0, 4, 3, 5, 2, 7},
    {9, 4, 5, 3, 1, 2, 6, 8, 7, 0}, {4, 2, 8, 6, 5, 7, 3, 9, 0, 1},
    {2, 7, 9, 3, 8, 0, 6, 4, 1, 5}, {7, 0, 4, 6, 9, 1, 3, 2, 5, 8},
};

int verhoeff(const char* s, bool validate, bool verbose) {
    if (verbose) {
        const char* t = validate ? "Validation" : "Check digit";
        printf("%s calculations for '%s':\n\n", t, s);
        puts(u8" i  n\xE1\xB5\xA2  p[i,n\xE1\xB5\xA2]  c");
        puts("------------------");
    }
    int len = strlen(s);
    if (validate)
        --len;
    int c = 0;
    for (int i = len; i >= 0; --i) {
        int ni = (i == len && !validate) ? 0 : s[i] - '0';
        assert(ni >= 0 && ni < 10);
        int pi = p[(len - i) % 8][ni];
        c = d[c][pi];
        if (verbose)
            printf("%2d  %d      %d     %d\n", len - i, ni, pi, c);
    }
    if (verbose && !validate)
        printf("\ninv[%d] = %d\n", c, inv[c]);
    return validate ? c == 0 : inv[c];
}

int main() {
    const char* ss[3] = {"236", "12345", "123456789012"};
    for (int i = 0; i < 3; ++i) {
        const char* s = ss[i];
        bool verbose = i < 2;
        int c = verhoeff(s, false, verbose);
        printf("\nThe check digit for '%s' is '%d'.\n", s, c);
        int len = strlen(s);
        char sc[len + 2];
        strncpy(sc, s, len + 2);
        for (int j = 0; j < 2; ++j) {
            sc[len] = (j == 0) ? c + '0' : '9';
            int v = verhoeff(sc, true, verbose);
            printf("\nThe validation for '%s' is %s.\n", sc,
                   v ? "correct" : "incorrect");
        }
    }
    return 0;
}
