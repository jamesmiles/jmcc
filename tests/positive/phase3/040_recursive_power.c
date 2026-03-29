// TEST: recursive_power
// DESCRIPTION: Recursive power function (2^10 = 1024 mod 256 = 0)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 3

int power(int base, int exp) {
    if (exp == 0) return 1;
    return base * power(base, exp - 1);
}

int main(void) {
    int result = power(2, 10);
    return result - 1024;
}
