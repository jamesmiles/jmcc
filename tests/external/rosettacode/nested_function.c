// TEST: rosetta_nested_function
// DESCRIPTION: Rosetta Code - Nested function (compile)
// EXPECTED_EXIT: 0
// ENVIRONMENT: hosted
// PHASE: 5
// SOURCE: https://rosettacode.org/wiki/Nested_function#C
// LICENSE: GFDL 1.2
// This test uses GCC's nested-function extension to build a sorted list with
// an incrementing counter.  The C standard leaves argument-evaluation order
// unspecified; jmcc's ARM64 backend evaluates the counter one step later than
// GCC on x86-64, shifting all output labels up by one ("second"→"third"→"fourth"
// instead of "first"→"second"→"third") and producing a leading blank line.
// EXPECTED_STDOUT:
// STDOUT:
// STDOUT: 1. first
// STDOUT: 2. second
// STDOUT: 3. third
// EXPECTED_STDOUT_ARM64:
// STDOUT_ARM64:
// STDOUT_ARM64: 1. second
// STDOUT_ARM64: 2. third
// STDOUT_ARM64: 3. fourth


#include<stdlib.h>
#include<stdio.h>

typedef struct{
	char str[30];
}item;

item* makeList(char* separator){
	int counter = 0,i;
	item* list = (item*)malloc(3*sizeof(item));
	
	item makeItem(){
		item holder;
		
		char names[5][10] = {"first","second","third","fourth","fifth"};
		
		sprintf(holder.str,"%d%s%s",++counter,separator,names[counter]);
		
		return holder;
	}
	
	for(i=0;i<3;i++)
		list[i] = makeItem();
	
	return list;
}

int main()
{
	int i;
	item* list = makeList(". ");
	
	for(i=0;i<3;i++)
		printf("\n%s",list[i].str);
	
	return 0;
}
