// TEST: ctest_00021
// DESCRIPTION: c-testsuite test 00021
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
foo(int a, int b)
{
	return 2 + a - b;
}

int
main()
{
	return foo(1, 3);
}

