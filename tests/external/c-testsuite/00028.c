// TEST: ctest_00028
// DESCRIPTION: c-testsuite test 00028
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int x;
	
	x = 1;
	x = x & 3;
	return x - 1;
}

