// TEST: ctest_00090
// DESCRIPTION: c-testsuite test 00090
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int a[3] = {0, 1, 2};

int
main()
{
	if (a[0] != 0)
		return 1;
	if (a[1] != 1)
		return 2;
	if (a[2] != 2)
		return 3;
	
	return 0;
}
