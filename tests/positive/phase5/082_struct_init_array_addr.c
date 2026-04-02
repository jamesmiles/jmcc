// TEST: struct_init_array_addr
// DESCRIPTION: &array[index] in struct initializer (Doom's chat_macros[] crash)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: val0=10
// STDOUT: val2=30
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's defaults[] has entries like:
     {"chatmacro0", (int *) &chat_macros[0], (int) HUSTR_CHATMACRO0}
   The &chat_macros[0] expression (address of array element) in a
   struct initializer is not handled by JMCC — it emits NULL instead
   of the address. This causes a segfault when M_LoadDefaults writes
   through the NULL pointer. Entries 31-39 in defaults[] are all NULL. */

int printf(const char *fmt, ...);

typedef struct {
    char *name;
    int *location;
    int defaultvalue;
} config_t;

int values[4];

config_t configs[] = {
    {"val0", &values[0], 10},
    {"val1", &values[1], 20},
    {"val2", &values[2], 30},
    {"val3", &values[3], 40},
};

int main(void) {
    int num = sizeof(configs) / sizeof(configs[0]);
    int i;
    for (i = 0; i < num; i++) {
        *configs[i].location = configs[i].defaultvalue;
    }
    printf("val0=%d\n", values[0]);
    printf("val2=%d\n", values[2]);
    return 0;
}
