// TEST: ctest_00069
// DESCRIPTION: c-testsuite test 00069
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#if 0
X
#elif 0
X
#elif 1
int x = 0;
#endif

int
main()
{
	return x;
}
