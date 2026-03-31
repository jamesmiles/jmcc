// TEST: switch_enum
// DESCRIPTION: Switch on enum values (Doom's weapontype_t pattern)
// EXPECTED_EXIT: 0
// EXPECTED_STDOUT: shotgun
// STDOUT: chaingun
// STDOUT: rocket
// ENVIRONMENT: hosted
// PHASE: 5

int printf(const char *fmt, ...);

typedef enum {
    wp_fist,
    wp_pistol,
    wp_shotgun,
    wp_chaingun,
    wp_missile,
    wp_plasma,
    wp_bfg,
    wp_chainsaw,
    wp_supershotgun,
    NUMWEAPONS
} weapontype_t;

const char *weapon_name(weapontype_t w) {
    switch (w) {
        case wp_fist: return "fist";
        case wp_pistol: return "pistol";
        case wp_shotgun: return "shotgun";
        case wp_chaingun: return "chaingun";
        case wp_missile: return "rocket";
        case wp_plasma: return "plasma";
        case wp_bfg: return "bfg";
        case wp_chainsaw: return "chainsaw";
        case wp_supershotgun: return "super shotgun";
        default: return "unknown";
    }
}

int main(void) {
    printf("%s\n", weapon_name(wp_shotgun));
    printf("%s\n", weapon_name(wp_chaingun));
    printf("%s\n", weapon_name(wp_missile));
    return 0;
}
