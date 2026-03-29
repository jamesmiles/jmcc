// TEST: linked_list
// DESCRIPTION: Simple singly-linked list traversal using struct pointers
// EXPECTED_EXIT: 6
// ENVIRONMENT: hosted
// PHASE: 3
// STANDARD_REF: 6.7.2.1 (Structure specifiers)

struct Node {
    int value;
    struct Node *next;
};

int sum_list(struct Node *head) {
    int total = 0;
    struct Node *curr = head;
    while (curr != 0) {
        total = total + curr->value;
        curr = curr->next;
    }
    return total;
}

int main(void) {
    struct Node c;
    c.value = 3;
    c.next = 0;
    struct Node b;
    b.value = 2;
    b.next = &c;
    struct Node a;
    a.value = 1;
    a.next = &b;
    return sum_list(&a);
}
