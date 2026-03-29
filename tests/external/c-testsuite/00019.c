// TEST: ctest_00019
// DESCRIPTION: c-testsuite test 00019
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	struct S { struct S *p; int x; } s;
	
	s.x = 0;
	s.p = &s;
	return s.p->p->p->p->p->x;
}

