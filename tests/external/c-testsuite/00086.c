// TEST: ctest_00086
// DESCRIPTION: c-testsuite test 00086
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	short x;
	
	x = 0;
	x = x + 1;
	if (x != 1)
		return 1;
	return 0;
}
