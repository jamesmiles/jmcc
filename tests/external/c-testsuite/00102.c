// TEST: ctest_00102
// DESCRIPTION: c-testsuite test 00102
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int x;
	
	x = 1;
	if ((x << 1) != 2)
		return 1;
	
	return 0;
}
