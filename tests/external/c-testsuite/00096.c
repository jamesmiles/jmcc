// TEST: ctest_00096
// DESCRIPTION: c-testsuite test 00096
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int x, x = 3, x;

int
main()
{
	if (x != 3)
		return 0;

	x = 0;
	return x;
}

