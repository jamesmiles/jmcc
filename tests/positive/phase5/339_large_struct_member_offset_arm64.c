/* Regression: accessing a struct member at byte offset > 4095 generates:
 *   add x0, x0, #25716
 * ARM64 error: "expected compatible register, symbol or integer in range [0, 4095]"
 *
 * The ARM64 add-immediate instruction only encodes 12-bit immediates (0-4095,
 * optionally shifted left by 12). For larger offsets jmcc must load the
 * constant into a scratch register:
 *   movz x1, #25716
 *   add  x0, x0, x1
 *
 * Triggered by src/net_server.c which accesses clients[i].field where the
 * net_connect_t struct is 25768 bytes and the field is at offset 25716.
 */

typedef struct {
    char padding[5000]; /* push a field beyond offset 4095 */
    int value;
} large_t;

static large_t obj;

int get_value(void) {
    obj.value = 42;
    return obj.value;
}

int main(void) {
    return get_value() - 42;
}
