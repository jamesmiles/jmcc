// TEST: ctest_00088
// DESCRIPTION: c-testsuite test 00088
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int (*fptr)() = 0;


int
main()
{
	if (fptr)
		return 1;
	return 0;
}

