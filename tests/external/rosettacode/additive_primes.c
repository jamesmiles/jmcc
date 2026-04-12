// TEST: rosetta_additive_primes
// DESCRIPTION: Rosetta Code - Additive primes (bool array, digit sum, sieve)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Additive_primes#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: Rosetta Code: additive primes less than 500:
// STDOUT:    2   3   5   7  11  23  29  41  43  47
// STDOUT:   61  67  83  89 101 113 131 137 139 151
// STDOUT:  157 173 179 191 193 197 199 223 227 229
// STDOUT:  241 263 269 281 283 311 313 317 331 337
// STDOUT:  353 359 373 379 397 401 409 421 443 449
// STDOUT:  461 463 467 487
// STDOUT: Those were 54 additive primes.

#include <stdbool.h>
#include <stdio.h>
#include <string.h>

void memoizeIsPrime( bool * result, const int N )
{
    result[2] = true;
    result[3] = true;
    int prime[N];
    prime[0] = 3;
    int end = 1;
    for (int n = 5; n < N; n += 2)
    {
        bool n_is_prime = true;
        for (int i = 0; i < end; ++i)
        {
            const int PRIME = prime[i];
            if (n % PRIME == 0)
            {
                n_is_prime = false;
                break;
            }
            if (PRIME * PRIME > n)
            {
                break;
            }
        }
        if (n_is_prime)
        {
            prime[end++] = n;
            result[n] = true;
        }
    }
}/* memoizeIsPrime */

int sumOfDecimalDigits( int n )
{
    int sum = 0;
    while (n > 0)
    {
        sum += n % 10;
        n /= 10;
    }
    return sum;
}/* sumOfDecimalDigits */

int main( void )
{
    const int N = 500;

    printf( "Rosetta Code: additive primes less than %d:\n", N );

    bool is_prime[N];
    memset( is_prime, 0, sizeof(is_prime) );
    memoizeIsPrime( is_prime, N );

    printf( "   2" );
    int count = 1;
    for (int i = 3; i < N; i += 2)
    {
        if (is_prime[i] && is_prime[sumOfDecimalDigits( i )])
        {
            printf( "%4d", i );
            ++count;
            if ((count % 10) == 0)
            {
                printf( "\n" );
            }
        }
    }
    printf( "\nThose were %d additive primes.\n", count );
    return 0;
}/* main */
