// Bug 253: __builtin_add_overflow not implemented as intrinsic
// Used by SQLite's sqlite3AddInt64 for overflow-safe integer arithmetic
#include <stdio.h>
#include <stdint.h>

int main(void) {
    long long a, b, result;

    // No overflow: INT64_MAX + (-INT64_MAX) = 0
    a = 9223372036854775807LL;
    b = -9223372036854775807LL;
    result = 0;
    int ov1 = __builtin_add_overflow(a, b, &result);
    if (ov1 != 0 || result != 0LL) {
        printf("FAIL: INT64_MAX + (-INT64_MAX): ov=%d result=%lld\n", ov1, result);
        return 1;
    }

    // Overflow: INT64_MAX + 1 overflows
    a = 9223372036854775807LL;
    b = 1LL;
    result = 0;
    int ov2 = __builtin_add_overflow(a, b, &result);
    if (ov2 == 0) {
        printf("FAIL: INT64_MAX + 1 should overflow, got result=%lld\n", result);
        return 1;
    }

    // No overflow: small values
    a = 100LL; b = 200LL; result = 0;
    int ov3 = __builtin_add_overflow(a, b, &result);
    if (ov3 != 0 || result != 300LL) {
        printf("FAIL: 100+200: ov=%d result=%lld\n", ov3, result);
        return 1;
    }

    printf("ok\n");
    return 0;
}
