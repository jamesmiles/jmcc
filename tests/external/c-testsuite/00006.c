// TEST: ctest_00006
// DESCRIPTION: c-testsuite test 00006
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int x;

	x = 50;
	while (x)
		x = x - 1;
	return x;
}
