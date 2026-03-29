// TEST: ctest_00152
// DESCRIPTION: c-testsuite test 00152
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#undef  line
#define line 1000

#line line
#if 1000 != __LINE__
	#error "  # line line" not work as expected
#endif

int
main()
{
	return 0;
}
