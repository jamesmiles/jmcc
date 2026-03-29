// TEST: ctest_00149
// DESCRIPTION: c-testsuite test 00149
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

struct S { int a; int b; };
struct S *s = &(struct S) { 1, 2 };

int
main()
{
	if(s->a != 1)
		return 1;
	if(s->b != 2)
		return 2;
	return 0;
}
