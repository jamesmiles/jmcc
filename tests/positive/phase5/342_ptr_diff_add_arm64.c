// Test: pointer + (pointer - pointer) uses 64-bit arithmetic on arm64
// On arm64, all pointers are >4GB; if the final add uses w-reg (32-bit),
// the result is truncated and the dereference segfaults.
// Derived from DEH_StructSHA1Sum pattern in Chocolate Doom.
#include <stdio.h>
#include <stdint.h>

static int base_arr[4] = {10, 20, 30, 40};
static int dst_arr[4]  = {100, 200, 300, 400};

int main(void) {
    uint8_t *base = (uint8_t *)&base_arr[0];
    uint8_t *field = (uint8_t *)&base_arr[2];      // offset = 8 bytes into base_arr
    uint8_t *structptr = (uint8_t *)&dst_arr[0];

    // location = structptr + (field - base) must use 64-bit add
    uint8_t *location = structptr + (field - base);
    int val = *((int *)location);                   // should be dst_arr[2] = 300
    printf("%d\n", val);
    return (val == 300) ? 0 : 1;
}
