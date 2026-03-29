// TEST: ctest_00118
// DESCRIPTION: c-testsuite test 00118
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	struct { int x; } s = { 0 };
	return s.x;
}
