// TEST: global_ptr_array_element_init
// DESCRIPTION: Global pointer initialized with &array[index] must point to correct element
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's g_game.c has: boolean* mousebuttons = &mousearray[1];
   This allows mousebuttons[-1] to access mousearray[0].
   If the global pointer is emitted as .zero (NULL) instead of
   being initialized with the array element address, accessing
   mousebuttons[mousebstrafe] segfaults in G_BuildTiccmd on
   the first game tick. */

int printf(const char *fmt, ...);

int arr[4] = {10, 20, 30, 40};
int *ptr = &arr[1];

int main(void) {
    if (ptr == 0) return 1;
    if (ptr[-1] != 10) return 2;
    if (ptr[0] != 20) return 3;
    if (ptr[1] != 30) return 4;
    printf("ok\n");
    return 0;
}
