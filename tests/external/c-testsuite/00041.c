// TEST: ctest_00041
// DESCRIPTION: c-testsuite test 00041
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

int
main() {
	int n;
	int t;
	int c;
	int p;

	c = 0;
	n = 2;
	while (n < 5000) {
		t = 2;
		p = 1;
		while (t*t <= n) {
			if (n % t == 0)
				p = 0;
			t++;
		}
		n++;
		if (p)
			c++;
	}
	if (c != 669)
		return 1;
	return 0;
}

