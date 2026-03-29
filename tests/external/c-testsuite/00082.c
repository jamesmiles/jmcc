// TEST: ctest_00082
// DESCRIPTION: c-testsuite test 00082
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	unsigned long long x;
	
	x = 0;
	x = x + 1;
	if (x != 1)
		return 1;
	return 0;
}
