// TEST: ctest_00142
// DESCRIPTION: c-testsuite test 00142
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#if defined(FOO)
int a;
#elif !defined(FOO) && defined(BAR)
int b;
#elif !defined(FOO) && !defined(BAR)
int c;
#else
int d;
#endif

int
main(void)
{
	return c;
}
