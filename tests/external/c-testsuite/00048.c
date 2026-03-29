// TEST: ctest_00048
// DESCRIPTION: c-testsuite test 00048
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

struct S {int a; int b;};
struct S s = { .b = 2, .a = 1};

int
main()
{
	if(s.a != 1)
		return 1;
	if(s.b != 2)
		return 2;
	return 0;
}
