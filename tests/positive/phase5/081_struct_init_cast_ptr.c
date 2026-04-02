// TEST: struct_init_cast_ptr
// DESCRIPTION: Struct initializer with (int*) cast on address-of (Doom defaults[] crash)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: str=hello
// STDOUT: val=42
// ENVIRONMENT: hosted
// PHASE: 5

/* Doom's defaults[] array has entries like:
     {"sndserver", (int *) &sndserver_filename, (int) "sndserver"}
   The (int*) cast on &sndserver_filename stores a char** as int*.
   JMCC silently drops cast expressions in struct initializers,
   emitting .zero instead of the address — causing NULL pointer crash. */

int printf(const char *fmt, ...);

typedef struct {
    char *name;
    int *location;
    int defaultvalue;
} config_t;

char *my_string;
int my_value;

config_t configs[] = {
    {"value", &my_value, 42},
    {"string", (int *) &my_string, 0},
};

int main(void) {
    /* Set my_value through the location pointer */
    *configs[0].location = configs[0].defaultvalue;

    /* Set my_string through the cast pointer */
    *(char **)configs[1].location = "hello";

    printf("str=%s\n", my_string);
    printf("val=%d\n", my_value);
    return 0;
}
