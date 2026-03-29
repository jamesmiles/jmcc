// TEST: ctest_00129
// DESCRIPTION: c-testsuite test 00129
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 4

typedef struct s s;

struct s {
	struct s1 {
		int s;
		struct s2 {
			int s;
		} s1;
	} s;
} s2;

#define s s

int
main(void)
{
#undef s
	goto s;
	struct s s;
		{
			int s;
			return s;
		}
	return s.s.s + s.s.s1.s;
	s:
		{
			return 0;
		}
	return 1;
}
