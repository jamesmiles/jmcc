// TEST: rosetta_call_an_object_method
// DESCRIPTION: Rosetta Code - Call an object method (exit code mismatch)
// EXPECTED_EXIT: 49
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Call_an_object_method#C
// LICENSE: GFDL 1.2
// EXPECTED_STDOUT:
// STDOUT: Usage : /tmp/tmpi3xw00v8/g <non negative integer>


#include<stdlib.h>
#include<stdio.h>

typedef struct{
        int x;
        int (*funcPtr)(int);
}functionPair;

int factorial(int num){
        if(num==0||num==1)
                return 1;
        else
                return num*factorial(num-1);
}

int main(int argc,char** argv)
{
        functionPair response;

        if(argc!=2)
                return printf("Usage : %s <non negative integer>",argv[0]);
        else{
                response = (functionPair){.x = atoi(argv[1]),.funcPtr=&factorial};
                printf("\nFactorial of %d is %d\n",response.x,response.funcPtr(response.x));
        }
        return 0;
}
