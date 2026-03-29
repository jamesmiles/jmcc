// TEST: ctest_00043
// DESCRIPTION: c-testsuite test 00043
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

struct s {
    int x;
    struct {
        int y;
        int z;
    } nest;
};

int
main() {
    struct s v;
    v.x = 1;
    v.nest.y = 2;
    v.nest.z = 3;
    if (v.x + v.nest.y + v.nest.z != 6)
        return 1;
    return 0;
}

