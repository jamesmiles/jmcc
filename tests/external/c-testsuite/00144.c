// TEST: ctest_00144
// DESCRIPTION: c-testsuite test 00144
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main(void)
{
	int i, *q;
	void *p;

	i = i ? 0 : 0l;
	p = i ? (void *) 0 : 0;
	p = i ? 0 : (void *) 0;
	p = i ? 0 : (const void *) 0;
	q = i ? 0 : p;
	q = i ? p : 0;
	q = i ? q : 0;
	q = i ? 0 : q;

	return (int) q;
}
