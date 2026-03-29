// TEST: ctest_00076
// DESCRIPTION: c-testsuite test 00076
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	if(0 ? 1 : 0)
		return 1;
	if(1 ? 0 : 1)
		return 2;
	return 0;
}
