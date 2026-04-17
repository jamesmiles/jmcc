// TEST: rosetta_4_rings_or_4_squares_puzzle
// DESCRIPTION: Rosetta Code - 4-rings or 4-squares puzzle (compile)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/4-rings_or_4-squares_puzzle#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT:
// STDOUT: 4 7 1 3 2 6 5
// STDOUT: 6 4 1 5 2 3 7
// STDOUT: 3 7 2 1 5 4 6
// STDOUT: 5 6 2 3 1 7 4
// STDOUT: 7 3 2 5 1 4 6
// STDOUT: 4 5 3 1 6 2 7
// STDOUT: 6 4 5 1 2 7 3
// STDOUT: 7 2 6 1 3 5 4
// STDOUT:
// STDOUT: 8 unique solutions in 1 to 7
// STDOUT:
// STDOUT: 7 8 3 4 5 6 9
// STDOUT: 8 7 3 5 4 6 9
// STDOUT: 9 6 4 5 3 7 8
// STDOUT: 9 6 5 4 3 8 7
// STDOUT:
// STDOUT: 4 unique solutions in 3 to 9
// STDOUT:
// STDOUT:
// STDOUT: 2860 non-unique solutions in 0 to 9


#include <stdio.h>

#define TRUE 1
#define FALSE 0

int a,b,c,d,e,f,g;
int lo,hi,unique,show;
int solutions;

void
bf()
{
    for (f = lo;f <= hi; f++)
        if ((!unique) ||
           ((f != a) && (f != c) && (f != d) && (f != g) && (f != e)))
            {
            b = e + f - c;
            if ((b >= lo) && (b <= hi) &&
                   ((!unique) || ((b != a) && (b != c) &&
                   (b != d) && (b != g) && (b != e) && (b != f))))
                {
                solutions++;
                if (show)
                    printf("%d %d %d %d %d %d %d\n",a,b,c,d,e,f,g);
                }
            }
}


void
ge()
{
    for (e = lo;e <= hi; e++)
        if ((!unique) || ((e != a) && (e != c) && (e != d)))
            {
            g = d + e;
            if ((g >= lo) && (g <= hi) &&
                   ((!unique) || ((g != a) && (g != c) &&
                   (g != d) && (g != e))))
                bf();
            }
}

void
acd()
{
    for (c = lo;c <= hi; c++)
        for (d = lo;d <= hi; d++)
            if ((!unique) || (c != d))
                {
                a = c + d;
                if ((a >= lo) && (a <= hi) &&
                   ((!unique) || ((c != 0) && (d != 0))))
                    ge();
                }
}


void
foursquares(int plo,int phi, int punique,int pshow)
{
    lo = plo;
    hi = phi;
    unique = punique;
    show = pshow;
    solutions = 0;

    printf("\n");

    acd();

    if (unique)
        printf("\n%d unique solutions in %d to %d\n",solutions,lo,hi);
    else
        printf("\n%d non-unique solutions in %d to %d\n",solutions,lo,hi);
}

main()
{
    foursquares(1,7,TRUE,TRUE);
    foursquares(3,9,TRUE,TRUE);
    foursquares(0,9,FALSE,FALSE);
}
