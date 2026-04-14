// TEST: rosetta_cousin_primes
// DESCRIPTION: Rosetta Code - Cousin primes (wrong count - incorrectly identifies 1001 as prime)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Cousin_primes#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT:    3:    7
// STDOUT:    7:   11
// STDOUT:   13:   17
// STDOUT:   19:   23
// STDOUT:   37:   41
// STDOUT:   43:   47
// STDOUT:   67:   71
// STDOUT:   79:   83
// STDOUT:   97:  101
// STDOUT:  103:  107
// STDOUT:  109:  113
// STDOUT:  127:  131
// STDOUT:  163:  167
// STDOUT:  193:  197
// STDOUT:  223:  227
// STDOUT:  229:  233
// STDOUT:  277:  281
// STDOUT:  307:  311
// STDOUT:  313:  317
// STDOUT:  349:  353
// STDOUT:  379:  383
// STDOUT:  397:  401
// STDOUT:  439:  443
// STDOUT:  457:  461
// STDOUT:  463:  467
// STDOUT:  487:  491
// STDOUT:  499:  503
// STDOUT:  613:  617
// STDOUT:  643:  647
// STDOUT:  673:  677
// STDOUT:  739:  743
// STDOUT:  757:  761
// STDOUT:  769:  773
// STDOUT:  823:  827
// STDOUT:  853:  857
// STDOUT:  859:  863
// STDOUT:  877:  881
// STDOUT:  883:  887
// STDOUT:  907:  911
// STDOUT:  937:  941
// STDOUT:  967:  971
// STDOUT: There are 41 cousin prime pairs below 1000.

#include <stdio.h>
#include <string.h>

#define LIMIT 1000

void sieve(int max, char *s) {
    int p, k;
    memset(s, 0, max);
    for (p=2; p*p<=max; p++)
        if (!s[p]) 
            for (k=p*p; k<=max; k+=p) 
                s[k]=1;
}

int main(void) {
    char primes[LIMIT+1];
    int p, count=0;
    
    sieve(LIMIT, primes);
    for (p=2; p<=LIMIT; p++) {
        if (!primes[p] && !primes[p+4]) {
            count++;
            printf("%4d: %4d\n", p, p+4);
        }
    }
    
    printf("There are %d cousin prime pairs below %d.\n", count, LIMIT);
    return 0;
}
