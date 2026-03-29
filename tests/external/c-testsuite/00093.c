// TEST: ctest_00093
// DESCRIPTION: c-testsuite test 00093
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int a[] = {1, 2, 3, 4};

int
main()
{
	if (sizeof(a) != 4*sizeof(int))
		return 1;
	
	return 0;
}
