// TEST: ctest_00065
// DESCRIPTION: c-testsuite test 00065
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#define ADD(X, Y) (X + Y)


int
main()
{
	return ADD(1, 2) - 3;
}
