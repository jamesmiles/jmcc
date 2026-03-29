// TEST: ctest_00030
// DESCRIPTION: c-testsuite test 00030
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
f()
{
	return 100;
}

int
main()
{
	if (f() > 1000)
		return 1;
	if (f() >= 1000)
		return 1;
	if (1000 < f())
		return 1;
	if (1000 <= f())
		return 1;
	if (1000 == f())
		return 1;
	if (100 != f())
		return 1;
	return 0;
}

