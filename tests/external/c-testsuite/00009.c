// TEST: ctest_00009
// DESCRIPTION: c-testsuite test 00009
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int x;
	
	x = 1;
	x = x * 10;
	x = x / 2;
	x = x % 3;
	return x - 2;
}
