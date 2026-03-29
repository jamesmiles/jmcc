// TEST: ctest_00062
// DESCRIPTION: c-testsuite test 00062
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#ifdef FOO
	XXX
#ifdef BAR
	XXX
#endif
	XXX
#endif

#define FOO 1

#ifdef FOO

#ifdef FOO
int x = 0;
#endif

int
main()
{
	return x;
}
#endif



