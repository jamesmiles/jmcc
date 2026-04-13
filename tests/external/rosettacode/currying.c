// TEST: rosetta_currying
// DESCRIPTION: Rosetta Code - Currying (va_list typedef not recognized)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Currying#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT:
// STDOUT: Sum of factorials of [1,5] : 153
// STDOUT: Sum of factorials of [3,5] : 150
// STDOUT: Sum of factorials of [1,3] : 9


#include<stdarg.h>
#include<stdio.h>

long int factorial(int n){
    if(n>1)
        return n*factorial(n-1);
    return 1;
}

long int sumOfFactorials(int num,...){
    va_list vaList;
    long int sum = 0;
    
    va_start(vaList,num);
    
    while(num--)
        sum += factorial(va_arg(vaList,int));
    
    va_end(vaList);
    
    return sum;
}

int main()
{
    printf("\nSum of factorials of [1,5] : %ld",sumOfFactorials(5,1,2,3,4,5));
    printf("\nSum of factorials of [3,5] : %ld",sumOfFactorials(3,3,4,5));
    printf("\nSum of factorials of [1,3] : %ld",sumOfFactorials(3,1,2,3));
    
    return 0;
}

