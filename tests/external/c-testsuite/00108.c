// TEST: ctest_00108
// DESCRIPTION: c-testsuite test 00108
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int foo(void);
int foo(void);
#define FOO 0

int
main()
{
	return FOO;
}
