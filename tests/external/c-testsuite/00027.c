// TEST: ctest_00027
// DESCRIPTION: c-testsuite test 00027
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int x;
	
	x = 1;
	x = x | 4;
	return x - 5;
}

