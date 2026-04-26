// TEST: af_packet_sockaddr_ll
// DESCRIPTION: AF_PACKET and struct sockaddr_ll must be available via netpacket/packet.h (used by CPython socketmodule.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <sys/socket.h>
#include <netpacket/packet.h>
#include <stdio.h>

int main(void) {
    int af = AF_PACKET;
    struct sockaddr_ll sa;
    sa.sll_family = AF_PACKET;
    if (af <= 0) return 1;
    (void)sa;
    printf("OK\n");
    return 0;
}
