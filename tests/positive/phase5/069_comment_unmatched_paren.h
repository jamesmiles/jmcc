#ifndef COMMENT_PAREN_H
#define COMMENT_PAREN_H

// Internal parameters for sound rendering.
// These have been taken from the DOS version,
//  but are not (yet) supported with Linux
//  (e.g. no sound volume adjustment with menu.

// These are not used, but should be (menu).
// From m_menu.c:
//  Sound FX volume has default, 0 - 15

typedef struct {
    int sfx_volume;
    int music_volume;
} sound_config_t;

int get_default_volume(void);

#endif
