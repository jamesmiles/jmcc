// TEST: ctest_00070
// DESCRIPTION: c-testsuite test 00070
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#ifndef DEF
int x = 0;
#endif

#define DEF

#ifndef DEF
X
#endif

int
main()
{
	return x;
}
