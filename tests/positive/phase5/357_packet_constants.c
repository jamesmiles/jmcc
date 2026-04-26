// TEST: packet_constants
// DESCRIPTION: PACKET_HOST, PACKET_BROADCAST, PACKET_MULTICAST, PACKET_OTHERHOST, PACKET_OUTGOING must be defined in netpacket/packet.h (CPython socketmodule.c)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: OK
// ENVIRONMENT: hosted
#include <netpacket/packet.h>
#include <stdio.h>

int main(void) {
    int a = PACKET_HOST;
    int b = PACKET_BROADCAST;
    int c = PACKET_MULTICAST;
    int d = PACKET_OTHERHOST;
    int e = PACKET_OUTGOING;
    (void)a;(void)b;(void)c;(void)d;(void)e;
    printf("OK\n");
    return 0;
}
