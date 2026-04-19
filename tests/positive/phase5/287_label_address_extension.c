// TEST: label_address_extension
// DESCRIPTION: GCC &&label extension (address of a label for computed goto) must work
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>

int main(void) {
    /* GCC computed goto with &&label */
    static void *dispatch[] = { &&L_zero, &&L_one, &&L_two };
    int x = 1;
    goto *dispatch[x];
  L_zero: printf("zero\n"); return 1;
  L_one:  printf("OK\n"); return 0;
  L_two:  printf("two\n"); return 1;
}
