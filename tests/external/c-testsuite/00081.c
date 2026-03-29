// TEST: ctest_00081
// DESCRIPTION: c-testsuite test 00081
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	long long x;
	
	x = 0;
	x = x + 1;
	if (x != 1)
		return 1;
	return 0;
}
