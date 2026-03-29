// TEST: ctest_00047
// DESCRIPTION: c-testsuite test 00047
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

struct { int a; int b; int c; } s = {1, 2, 3};

int
main()
{
	if (s.a != 1)
		return 1;
	if (s.b != 2)
		return 2;
	if (s.c != 3)
		return 3;

	return 0;
}
