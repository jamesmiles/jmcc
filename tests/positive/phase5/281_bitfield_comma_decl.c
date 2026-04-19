// TEST: bitfield_comma_decl
// DESCRIPTION: struct bitfield members with comma-separated declarators must work (e.g., uint8_t a:4, b:4)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <stdio.h>
#include <stdint.h>
struct tcp_info {
    uint8_t tcpi_options;
    uint8_t tcpi_snd_wscale : 4, tcpi_rcv_wscale : 4;
    uint32_t tcpi_rto;
};
int main(void) {
    struct tcp_info t;
    t.tcpi_snd_wscale = 3;
    t.tcpi_rcv_wscale = 5;
    t.tcpi_rto = 100;
    if (t.tcpi_snd_wscale != 3) return 1;
    if (t.tcpi_rcv_wscale != 5) return 2;
    printf("OK\n");
    return 0;
}
