// TEST: ctest_00054
// DESCRIPTION: c-testsuite test 00054
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

enum E {
	x,
	y,
	z,
};

int
main()
{
	enum E e;

	if(x != 0)
		return 1;
	if(y != 1)
		return 2;
	if(z != 2)
		return 3;
	
	e = x;
	return e;
}

