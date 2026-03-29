// TEST: ctest_00038
// DESCRIPTION: c-testsuite test 00038
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int x, *p;

	if (sizeof(0) < 2)
		return 1;
	if (sizeof 0 < 2)
		return 1;
	if (sizeof(char) < 1)
		return 1;
	if (sizeof(int) - 2 < 0)
		return 1;
	if (sizeof(&x) != sizeof p)
		return 1;
	return 0;
}
