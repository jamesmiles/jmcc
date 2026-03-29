// TEST: ctest_00103
// DESCRIPTION: c-testsuite test 00103
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main()
{
	int x;
	void *foo;
	void **bar;
	
	x = 0;
	
	foo = (void*)&x;
	bar = &foo;
	
	return **(int**)bar;
}
