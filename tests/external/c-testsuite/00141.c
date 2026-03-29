// TEST: ctest_00141
// DESCRIPTION: c-testsuite test 00141
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

#define CAT(x,y) x ## y
#define XCAT(x,y) CAT(x,y)
#define FOO foo
#define BAR bar

int
main(void)
{
	int foo, bar, foobar;

	CAT(foo,bar) = foo + bar;
	XCAT(FOO,BAR) = foo + bar;
	return 0;
}
