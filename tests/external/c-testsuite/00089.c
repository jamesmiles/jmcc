// TEST: ctest_00089
// DESCRIPTION: c-testsuite test 00089
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
zero()
{
	return 0;
}

struct S
{
	int (*zerofunc)();
} s = { &zero };

struct S *
anon()
{
	return &s;
}

typedef struct S * (*fty)();

fty
go()
{
	return &anon;
}

int
main()
{
	return go()()->zerofunc();
}
