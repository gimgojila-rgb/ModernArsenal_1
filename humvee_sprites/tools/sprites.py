"""Hand-placed pixel maps for hard mechanical parts (M4A1 method: measured, then placed cell by cell)."""
PAL = {
    '0': ('black', 0), 'k': ('black', 1), 'K': ('black', 2), 'L': ('black', 3), 'M': ('black', 4),
    's': ('steel', 2), 'S': ('steel', 3), 'T': ('steel', 4), 'U': ('steel', 5), 'V': ('steel', 6),
    'q': ('rust', 1), 'r': ('rust', 2), 'R': ('rust', 3), 'Q': ('rust', 4), 'W': ('rust', 5),
    'a': ('alu', 1), 'A': ('alu', 2), 'B': ('alu', 3), 'C': ('alu', 4), 'D': ('alu', 5),
    'w': ('white', 1), 'x': ('white', 2), 'y': ('yellow', 2), 'Y': ('yellow', 3),
    'o': ('olive', 0), '1': ('olive', 1), '2': ('olive', 2), '3': ('olive', 3), '4': ('olive', 4), '5': ('olive', 5), '6': ('olive', 6),
    'g': ('green', 2), 'G': ('green', 1), 'm': ('amber', 3), 'e': ('red', 3), 'E': ('red', 4),
    'c': ('chassis', 1), 'h': ('chassis', 2), 'H': ('chassis', 3), 'J': ('chassis', 4),
    't': ('tan', 1), 'u': ('tan', 2), 'v': ('tan', 3), 'z': ('tan', 4),
}

# 6.5L V8 turbo diesel, seen from the right. top-left = ref (75, 23). cols 0..25 -> x 75..100
ENGINE = [
    "..KL.......................",
    "..KL...CCCyCCCCC........LLL",
    "..KL..MMMMMMMMMMMMMKKKKKSTs",
    "ABBBAkLKLKLKLKLKLKLBCBKksTs",
    "BDCCBkkkkkkkkkkkkkkCDCLkTsT",
    "RQRRrkTTTTTTTTTTTTTABAKksTs",
    "rRRRqkQRRQRRQRRQRRQAKALkTsT",
    ".Rr.SSrrrrrrrrrrrrrAKALksTs",
    ".Rr.TTTTTTTTTTTTTTTAKAKkTsT",
    ".Rr.SsSsSUSsSsSsUsSKMKLksTs",
    ".Rr.SsSsSsSsSsSsSsSMLMKkTsT",
    ".Rr.sssssssssssxwssKMKKksTs",
    ".Rr..LLLLLLLLLLLLL....KkLLL",
    ".Rr...KKKMKKKKKKK..........",
    ".rq........................",
]

# bucket seat, side view (backrest at the rear/left). 16 x 14
SEAT = [
    "..0000..........",
    ".066540.........",
    ".055430.........",
    ".055430.........",
    "..055430........",
    "..054430........",
    "..054430........",
    "..054320........",
    "..054320........",
    "...05432000000..",
    "...054326666650.",
    "...054325555540.",
    "...044333333320.",
    "....00000000000.",
]

# steering wheel on the far side, rim seen at an angle + column. 8 x 9
STEER = [
    ".0KK0....",
    "0L..K0...",
    "0K...K0..",
    ".0K..K0..",
    ".0K..LK0.",
    "..0K.0KK.",
    "..0KKK0K.",
    "...000.0K",
    ".......0K",
]

# SINCGARS radio stack in its mount, 11 x 9
RADIO = [
    "00000000000",
    "0TTTTTTTTT0",
    "0s0000000s0",
    "0s0556550s0",
    "0s03gK3K30s",
    "0s0000000s0",
    "0s0445440s0",
    "0s03K3K3m0s",
    "00000000000",
]
