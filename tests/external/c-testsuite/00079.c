// TEST: ctest_00079
// DESCRIPTION: c-testsuite test 00079
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#define x(y) ((y) + 1)

int
main()
{
	int x;
	int y;
	
	y = 0;
	x = x(y);
	
	if(x != 1)
		return 1;
	
	return 0;
}

