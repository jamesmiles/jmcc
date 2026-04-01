// TEST: lvalue_after_switch
// DESCRIPTION: Complex Doom stair-builder pattern with struct/union/pointer subtraction
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: ok=0
// STDOUT: speed=4
// STDOUT: idx=1
// STDOUT: done
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);
void *malloc(unsigned long size);
void free(void *ptr);

typedef void (*actionf_p1)(void *);

typedef union {
    void (*acv)(void);
    actionf_p1 acp1;
} actionf_t;

typedef struct thinker_s {
    struct thinker_s *prev;
    struct thinker_s *next;
    actionf_t function;
} thinker_t;

typedef struct {
    int floorpic;
    void *specialdata;
} sector_t;

typedef struct {
    thinker_t thinker;
    int direction;
    int speed;
    int floordestheight;
    sector_t *sector;
} floormove_t;

typedef enum {
    build8,
    turbo16
} stair_e;

void T_MoveFloor(void *p) { (void)p; }

sector_t sectors[4];

int main(void) {
    int ok;
    int speed;
    int stairsize;
    int height = 0;
    int newsecnum;
    stair_e type = turbo16;
    sector_t *sec;
    sector_t *tsec;
    floormove_t *floor;

    sectors[0].floorpic = 1;
    sectors[1].floorpic = 1;
    sec = &sectors[0];

    floor = (floormove_t *)malloc(sizeof(*floor));
    floor->thinker.function.acp1 = (actionf_p1)T_MoveFloor;
    floor->direction = 1;
    floor->sector = sec;

    switch (type) {
      case build8:
        speed = 1;
        stairsize = 8;
        break;
      case turbo16:
        speed = 4;
        stairsize = 16;
        break;
    }

    floor->speed = speed;
    height = sec->floorpic + stairsize;
    floor->floordestheight = height;

    tsec = &sectors[1];
    newsecnum = tsec - sectors;

    do {
        ok = 0;
        if (newsecnum > 0) {
            ok = 1;
            newsecnum = 0;
        }
    } while (ok);

    printf("ok=%d\n", ok);
    printf("speed=%d\n", speed);
    printf("idx=%d\n", (int)(tsec - sectors));
    printf("done\n");
    free(floor);
    return 0;
}
