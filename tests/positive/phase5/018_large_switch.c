// TEST: large_switch
// DESCRIPTION: 50+ case switch statement (Doom's P_UseSpecialLine pattern)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: case 1: open door
// STDOUT: case 25: raise floor
// STDOUT: case 50: lights out
// STDOUT: default: unknown
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

const char *dispatch(int line_special) {
    switch (line_special) {
        case 1: return "open door";
        case 2: return "close door";
        case 3: return "open locked door";
        case 4: return "raise door";
        case 5: return "raise floor";
        case 6: return "fast crush ceiling";
        case 7: return "build stairs";
        case 8: return "build stairs turbo";
        case 9: return "donut";
        case 10: return "platform down wait up";
        case 11: return "exit level";
        case 12: return "light turn on";
        case 13: return "light turn on 255";
        case 14: return "raise floor 32";
        case 15: return "raise floor 24";
        case 16: return "close door 30";
        case 17: return "start light strobing";
        case 18: return "raise floor nearest";
        case 19: return "lower floor";
        case 20: return "raise floor lowest ceiling";
        case 21: return "platform lowest and change";
        case 22: return "raise floor nearest and change";
        case 23: return "lower floor to lowest";
        case 24: return "raise floor crush";
        case 25: return "raise floor";
        case 26: return "doors open blue";
        case 27: return "doors open yellow";
        case 28: return "doors open red";
        case 29: return "raise door";
        case 30: return "raise floor texture";
        case 31: return "door open";
        case 32: return "door open blue";
        case 33: return "door open red";
        case 34: return "door open yellow";
        case 35: return "lights very dark";
        case 36: return "lower floor turbo";
        case 37: return "lower floor and change";
        case 38: return "lower floor to lowest";
        case 39: return "teleport";
        case 40: return "raise ceiling lower floor";
        case 41: return "ceiling crush and raise";
        case 42: return "close door";
        case 43: return "ceiling lower to floor";
        case 44: return "ceiling crush raise silent";
        case 45: return "lower floor highest floor";
        case 46: return "door open";
        case 47: return "raise floor nearest and change 2";
        case 48: return "scroll wall left";
        case 49: return "ceiling crush stop";
        case 50: return "lights out";
        case 51: return "secret exit";
        case 52: return "exit level";
        default: return "unknown";
    }
}

int main(void) {
    printf("case 1: %s\n", dispatch(1));
    printf("case 25: %s\n", dispatch(25));
    printf("case 50: %s\n", dispatch(50));
    printf("default: %s\n", dispatch(99));
    return 0;
}
