// TEST: ctest_00037
// DESCRIPTION: c-testsuite test 00037
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int x[2];
	int *p;
	
	x[1] = 7;
	p = &x[0];
	p = p + 1;
	
	if(*p != 7)
		return 1;
	if(&x[1] - &x[0] != 1)
		return 1;
	
	return 0;
}
