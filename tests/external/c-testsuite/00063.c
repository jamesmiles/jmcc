// TEST: ctest_00063
// DESCRIPTION: c-testsuite test 00063
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#define BAR 0
#ifdef BAR
	#ifdef FOO
		XXX
		#ifdef FOO
			XXX
		#endif
	#else
		#define FOO
		#ifdef FOO
			int x = BAR;
		#endif
	#endif
#endif

int
main()
{
	return BAR;
}
