// TEST: ctest_00111
// DESCRIPTION: c-testsuite test 00111
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	short s = 1;
	long l = 1;

	s -= l;
	return s;
}
