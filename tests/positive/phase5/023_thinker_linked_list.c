// TEST: thinker_linked_list
// DESCRIPTION: Doom's thinker pattern - self-referential struct with linked list traversal
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: node 1
// STDOUT: node 2
// STDOUT: node 3
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

typedef union {
    void (*acv)(void);
    void (*acp1)(void *);
} actionf_t;

typedef struct thinker_s {
    struct thinker_s *prev;
    struct thinker_s *next;
    actionf_t function;
    int id;
} thinker_t;

int main(void) {
    thinker_t head;
    thinker_t n1, n2, n3;

    n1.id = 1;
    n2.id = 2;
    n3.id = 3;

    /* Build circular linked list (Doom pattern) */
    head.next = &n1;
    n1.prev = &head;
    n1.next = &n2;
    n2.prev = &n1;
    n2.next = &n3;
    n3.prev = &n2;
    n3.next = &head;
    head.prev = &n3;

    /* Traverse */
    thinker_t *cur = head.next;
    while (cur != &head) {
        printf("node %d\n", cur->id);
        cur = cur->next;
    }

    return 0;
}
