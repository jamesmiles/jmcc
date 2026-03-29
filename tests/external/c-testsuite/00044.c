// TEST: ctest_00044
// DESCRIPTION: c-testsuite test 00044
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

struct T;

struct T {
	int x;
};

int
main()
{
	struct T v;
	{ struct T { int z; }; }
	v.x = 2;
	if(v.x != 2)
		return 1;
	return 0;
}
