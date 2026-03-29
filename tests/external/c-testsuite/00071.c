// TEST: ctest_00071
// DESCRIPTION: c-testsuite test 00071
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#define X 1
#undef X

#ifdef X
FAIL
#endif

int
main()
{
	return 0;
}
