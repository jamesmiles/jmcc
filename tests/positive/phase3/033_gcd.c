// TEST: gcd
// DESCRIPTION: GCD using Euclidean algorithm
// EXPECTED_EXIT: 12
// ENVIRONMENT: hosted
// PHASE: 3

int gcd(int a, int b) {
    while (b != 0) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

int main(void) {
    return gcd(48, 36);
}
