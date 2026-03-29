// TEST: ctest_00109
// DESCRIPTION: c-testsuite test 00109
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int x = 0;
	int y = 1;
	if(x ? 1 : 0)
		return 1;
	if(y ? 0 : 1)
		return 2;
	return 0;
}
