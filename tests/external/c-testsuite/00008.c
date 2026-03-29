// TEST: ctest_00008
// DESCRIPTION: c-testsuite test 00008
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int x;

	x = 50;
	do 
		x = x - 1;
	while(x);
	return x;
}
