// TEST: ctest_00105
// DESCRIPTION: c-testsuite test 00105
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int i;

	for(i = 0; i < 10; i++)
		if (!i)
			continue;
	
	return 0;
}
