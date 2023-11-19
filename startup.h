#include <stdint.h>

typedef uint64_t ptr;

extern ptr scheme_entry(char *);

#define fxshift 2
#define fxmask 0x03
#define fxtag 0x00

#define chrmask 0x3F
#define chrshift 8
#define chrtag 0x0F

#define bool_f 0x2F
#define bool_t 0x6F
#define null 0x3F

#define char_tab 9
#define char_newline 10
#define char_vt 11
#define char_ff 12
#define char_return 13
#define char_space 32
