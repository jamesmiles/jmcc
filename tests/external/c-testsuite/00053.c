// TEST: ctest_00053
// DESCRIPTION: c-testsuite test 00053
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	struct T { int x; } s1;
	s1.x = 1;
	{
		struct T { int y; } s2;
		s2.y = 1;
		if (s1.x - s2.y != 0)
			return 1;
	}
	return 0;
}
