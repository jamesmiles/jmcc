// TEST: ctest_00116
// DESCRIPTION: c-testsuite test 00116
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
f(int f)
{
	return f;
}

int
main()
{
	return f(0);
}
