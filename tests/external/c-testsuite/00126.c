// TEST: ctest_00126
// DESCRIPTION: c-testsuite test 00126
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
        int x;

        x = 3;
        x = !x;
        x = !x;
        x = ~x;
        x = -x;
        if(x != 2)
                return 1;
        return 0;
}
