// TEST: ctest_00052
// DESCRIPTION: c-testsuite test 00052
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	struct T { int x; };
	{
		struct T s;
		s.x = 0;
		return s.x;
	}
}
