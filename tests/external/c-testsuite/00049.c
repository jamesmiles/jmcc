// TEST: ctest_00049
// DESCRIPTION: c-testsuite test 00049
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int x = 10;

struct S {int a; int *p;};
struct S s = { .p = &x, .a = 1};

int
main()
{
	if(s.a != 1)
		return 1;
	if(*s.p != 10)
		return 2;
	return 0;
}
