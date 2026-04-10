#include <stdio.h>

int usleep(int usec);

#define ROWS 24
#define COLS 60

int grid[ROWS][COLS];
int next[ROWS][COLS];

int count_neighbors(int r, int c) {
    int count = 0;
    int dr, dc;
    for (dr = -1; dr <= 1; dr++) {
        for (dc = -1; dc <= 1; dc++) {
            if (dr == 0 && dc == 0) continue;
            int nr = r + dr;
            int nc = c + dc;
            if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS) {
                count += grid[nr][nc];
            }
        }
    }
    return count;
}

void step(void) {
    int r, c;
    for (r = 0; r < ROWS; r++) {
        for (c = 0; c < COLS; c++) {
            int n = count_neighbors(r, c);
            if (grid[r][c]) {
                next[r][c] = (n == 2 || n == 3) ? 1 : 0;
            } else {
                next[r][c] = (n == 3) ? 1 : 0;
            }
        }
    }
    for (r = 0; r < ROWS; r++) {
        for (c = 0; c < COLS; c++) {
            grid[r][c] = next[r][c];
        }
    }
}

void print_grid(int gen) {
    printf("\033[H");
    printf("Generation: %d\n", gen);
    int r, c;
    for (r = 0; r < ROWS; r++) {
        for (c = 0; c < COLS; c++) {
            printf("%c", grid[r][c] ? '#' : '.');
        }
        printf("\n");
    }
}

int main(void) {
    /* Glider at top-left */
    grid[1][2] = 1;
    grid[2][3] = 1;
    grid[3][1] = 1;
    grid[3][2] = 1;
    grid[3][3] = 1;

    /* R-pentomino in the middle */
    grid[10][30] = 1;
    grid[10][31] = 1;
    grid[11][29] = 1;
    grid[11][30] = 1;
    grid[12][30] = 1;

    /* Blinker */
    grid[18][10] = 1;
    grid[18][11] = 1;
    grid[18][12] = 1;

    printf("\033[2J");

    int g;
    for (g = 0; ; g++) {
        print_grid(g);
        step();
        usleep(80000);
    }

    return 0;
}
