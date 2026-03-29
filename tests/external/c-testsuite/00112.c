// TEST: ctest_00112
// DESCRIPTION: c-testsuite test 00112
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	return "abc" == (void *)0;
}
