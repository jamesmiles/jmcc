// TEST: ctest_00055
// DESCRIPTION: c-testsuite test 00055
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

enum E {
	x,
	y = 2,
	z,
};

int
main()
{
	enum E e;

	if(x != 0)
		return 1;
	if(y != 2)
		return 2;
	if(z != 3)
		return 3;
	
	e = x;
	return e;
}

