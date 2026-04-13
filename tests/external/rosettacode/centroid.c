// TEST: rosetta_centroid
// DESCRIPTION: Rosetta Code - Centroid of N-dimensional points (VLA double output wrong)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Centroid_of_a_set_of_N-dimensional_points#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: {{1}, {2}, {3}} => Centroid: {2}
// STDOUT: {{8, 2}, {0, 0}} => Centroid: {4, 1}
// STDOUT: {{5, 5, 0}, {10, 10, 0}} => Centroid: {7.5, 7.5, 0}
// STDOUT: {{1, 3.1, 6.5}, {-2, -5, 3.4}, {-7, -4, 9}, {2, 0, 3}} => Centroid: {-1.5, -1.475, 5.475}
// STDOUT: {{0, 0, 0, 0, 1}, {0, 0, 0, 1, 0}, {0, 0, 1, 0, 0}, {0, 1, 0, 0, 0}} => Centroid: {0, 0.25, 0.25, 0.25, 0.25}

#include <stdio.h>

void centroid(int n, int d, double pts[n][d]) {
    int i, j;
    double ctr[d];
    for (j = 0; j < d; ++j) {
        ctr[j] = 0.0;
        for (i = 0; i < n; ++i) {
            ctr[j] += pts[i][j];
        }
        ctr[j] /= n;
    }
    printf("{");
    for (i = 0; i < n; ++i) {
        printf("{");
        for (j = 0; j < d; ++j) {
            printf("%g", pts[i][j]);
            if (j < d -1) printf(", ");
        }
        printf("}");
        if (i < n - 1) printf(", ");
    }
    printf("} => Centroid: {");
    for (j = 0; j < d; ++j) {
        printf("%g", ctr[j]);
        if (j < d-1) printf(", ");
    }
    printf("}\n");
}

int main() {
    double pts1[3][1] = { {1}, {2}, {3} };
    double pts2[2][2] = { {8, 2}, {0, 0} };
    double pts3[2][3] = { {5, 5, 0}, {10, 10, 0} };
    double pts4[4][3] = { {1, 3.1, 6.5}, {-2, -5, 3.4}, {-7, -4, 9}, {2, 0, 3} };
    double pts5[4][5] = { {0, 0, 0, 0, 1}, {0, 0, 0, 1, 0}, {0, 0, 1, 0, 0}, {0, 1, 0, 0, 0} };

    centroid(3, 1, pts1);
    centroid(2, 2, pts2);
    centroid(2, 3, pts3);
    centroid(4, 3, pts4);
    centroid(4, 5, pts5);
    return 0;
}