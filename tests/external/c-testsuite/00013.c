// TEST: ctest_00013
// DESCRIPTION: c-testsuite test 00013
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int x;
	int *p;
	
	x = 0;
	p = &x;
	return p[0];
}
