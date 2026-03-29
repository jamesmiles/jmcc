// TEST: ctest_00067
// DESCRIPTION: c-testsuite test 00067
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#if 1
int x = 0;
#endif

#if 0
int x = 1;
#if 1
 X
#endif
#ifndef AAA
 X
#endif
#endif

int main()
{
	return x;
}
