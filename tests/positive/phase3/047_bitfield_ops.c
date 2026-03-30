// TEST: bitfield_ops
// DESCRIPTION: Complex bitwise operations
// EXPECTED_EXIT: 170
// ENVIRONMENT: hosted
// PHASE: 3

int main(void) {
    unsigned int x = 0xAA;
    unsigned int y = 0xFF;
    unsigned int z = (x & y) | ((~x) & 0);
    return z;
}
