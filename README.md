# Computer Network HW 1
Socket Programming Practice

## Bingo Game
Implement a bingo game server and clinet with socket API.
Server creates game room for 5 players. One client is main culprit, other one clinet is copartner and the other 3 are AI players.

## Protocols
0: Main_culprit, 1: Copartner
role[0]: first arrival, role[1]: second arrival

turn[0]: first arrival, second arrival

when 2 human players are connected, server sends to these players 'game start' signal with initial game board.
client state changes from wait to game

# Game progress
    # i; 0>1>2>3>4>0>1>2>...
    # turn[i] = k, kth player playes
    # if k == 0 or 1 then server let player know that it's now player's turn (send to conn[k])
    # if role[k] == 0 then conn[k] is main_culprit, wait for 2 number, first one is bingo num, second is cheat
    # else if role[k] == 1 then conn[k] is copartner. server sends cheat number with start signal.
    # server checks if copartner plays correct way. if good, send 'turn end' signal. if not, replay signal.
    # if k is main_culprit, after receiving cheat num, server send ack (turn end) right after applying bingo result.
    # after applying bingo result, server sends to all players with updated bingo game board.
    # if bingo game ends, server sends 'turn end' signal to last player and send 'game finish' signal to all connected player (0, 1) instead of updated bingo board.
    # with winner information.

    # if the game is not end yet, i increases and next turn starts

    # protocol
    # Game Start:   'S R 00 00 00 ... 00' => 25 number with S prefix, R role (0 for main culprit, 1 for copartner)
    # Update board: 'U 00 00 00 ... 00' => 25 number with U prefix
    # Start turn:   'T'
    # Client ans:   '00'
    # Finish:       'F W' => W is winner (0 ~ 4) 0 is main culprit, 1 is copartner, 2~4: AI player.
    # Client compare W with own role. if match, you win! else if partner, ... else ai_n wins