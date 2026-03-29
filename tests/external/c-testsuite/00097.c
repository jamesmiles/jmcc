// TEST: ctest_00097
// DESCRIPTION: c-testsuite test 00097
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#define NULL ((void*)0)
#define NULL ((void*)0)

#define FOO(X, Y) (X + Y + Z)
#define FOO(X, Y) (X + Y + Z)

#define BAR(X, Y, ...) (X + Y + Z)
#define BAR(X, Y, ...) (X + Y + Z)

int
main()
{
	return 0;
}
