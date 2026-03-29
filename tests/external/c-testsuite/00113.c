// TEST: ctest_00113
// DESCRIPTION: c-testsuite test 00113
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int a = 0;
	float f = a + 1;

	return f == a;
}
