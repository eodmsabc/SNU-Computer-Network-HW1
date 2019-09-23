#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <vector>

#define NPLAYER 5
#define BINGO_SIZE 5
#define FOR(i,j,k) for(int i = (j); i < (k); i++)

char board[NPLAYER][BINGO_SIZE][BINGO_SIZE][2];

void board_init(void) {
    srand(time(NULL));
    FOR(p, 0, NPLAYER) {
        vector<int> used;
        FOR (i, 0, BINGO_SIZE) {
            FOR(j, 0, BINGO_SIZE) {
                int num = rand() % 99;
                board[p][i][j][0] = rand();
                board[p][i][j][1] = 0;
            }
        }
    }
}

int main(void) {
    const int port = 20395;
    int player = 3; // 3 pseudo player
    int server, client1, client2;
    printf("Server is running on port %d\n", port);
    return 0;
}