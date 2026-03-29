// TEST: ctest_00068
// DESCRIPTION: c-testsuite test 00068
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#if 0
X
#elif 1
int x = 0;
#else
X
#endif

int
main()
{
	return x;
}
