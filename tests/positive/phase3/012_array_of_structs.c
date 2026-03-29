// TEST: array_of_structs
// DESCRIPTION: Array of structs accessed via pointer arithmetic
// EXPECTED_EXIT: 6
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.7.2.1, 6.5.2.1 (Arrays and structs)

struct Pair {
    int a;
    int b;
};

int main(void) {
    struct Pair pairs[3];
    pairs[0].a = 1;
    pairs[0].b = 2;
    pairs[1].a = 3;
    pairs[1].b = 4;
    pairs[2].a = 5;
    pairs[2].b = 6;
    return pairs[2].b;
}
