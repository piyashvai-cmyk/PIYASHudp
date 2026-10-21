import aiohttp, asyncio, json, time, traceback, pytz, socket, struct, os, uuid, sys 
from colorama import Fore, Style
from datetime import datetime 
from Crypto.Cipher import AES 
from Crypto.Util.Padding import pad, unpad 
from protobuf_decoder.protobuf_decoder import Parser 
from all_cmds import MESSAGE_ID_TO_NAME
sys.dont_write_bytecode = True

AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

# global variables
chat_writer = None 
online_writer = None 
jwt_token = None 
nickname = None 
account_id = None 
game_version = None
release_version = None 
server_url = None 
clan_id = None 
owner_uid = None 
group_id = None 
team_owner_uid = None 
team_chat_code = None 
last_room_id = None
ghost_team_owner = None
ghost_team_id = None
is_sending_team_code_emote = False
last_status_packet = None
is_craftland = False

# configuration 
_accept_friend_request = True
_accept_clan_request = True
auth_world_chat = False
join_on_team_request_accept = True 
auto_ghost_on_leave = True

# owner config
bot_owner = "M4RUF"
name_text = """







































ﵥﵥﵥﵥﵥﵥﵥﵥ"""
name_v2 = f"""
.






[00FF00][B]WELCOME TO {bot_owner} TCP


"""

SKIP_UDP_LOG = [101, 108, 111, 117, 118, 121, 124, 135, 144, 216, 411, 412, 554, 694, 1221, 1343, 1617, 1710, 1900, 1901, 2001, 2012]

_DELTA = 0x9E3779B9
_ROUNDS = 16

_FIELD_SIZES = {0: 1, 1: 2, 2: 2, 3: 1, 4: 2}
_FIELD_NAMES = {0: "sendOption", 1: "cmd", 2: "orderId", 3: "flags", 4: "length"}

CRC7_TABLE = bytes([
    0, 9, 18, 27, 36, 45, 54, 63, 72, 65, 90, 83, 108, 101, 126, 119,
    25, 16, 11, 2, 61, 52, 47, 38, 81, 88, 67, 74, 117, 124, 103, 110,
    50, 59, 32, 41, 22, 31, 4, 13, 122, 115, 104, 97, 94, 87, 76, 69,
    43, 34, 57, 48, 15, 6, 29, 20, 99, 106, 113, 120, 71, 78, 85, 92,
    100, 109, 118, 127, 64, 73, 82, 91, 44, 37, 62, 55, 8, 1, 26, 19,
    125, 116, 111, 102, 89, 80, 75, 66, 53, 60, 39, 46, 17, 24, 3, 10,
    86, 95, 68, 77, 114, 123, 96, 105, 30, 23, 12, 5, 58, 51, 40, 33,
    79, 70, 93, 84, 107, 98, 121, 112, 7, 14, 21, 28, 35, 42, 49, 56,
    65, 72, 83, 90, 101, 108, 119, 126, 9, 0, 27, 18, 45, 36, 63, 54,
    88, 81, 74, 67, 124, 117, 110, 103, 16, 25, 2, 11, 52, 61, 38, 47,
    115, 122, 97, 104, 87, 94, 69, 76, 59, 50, 41, 32, 31, 22, 13, 4,
    106, 99, 120, 113, 78, 71, 92, 85, 34, 43, 48, 57, 6, 15, 20, 29,
    37, 44, 55, 62, 1, 8, 19, 26, 109, 100, 127, 118, 73, 64, 91, 82,
    60, 53, 46, 39, 24, 17, 10, 3, 116, 125, 102, 111, 80, 89, 66, 75,
    23, 30, 5, 12, 51, 58, 33, 40, 95, 86, 77, 68, 123, 114, 105, 96,
    14, 7, 28, 21, 42, 35, 56, 49, 70, 79, 84, 93, 98, 107, 112, 121,
])

RESPONSE_LAYOUTS = [
    [0, 4, 1, 3, 2],
    [0, 4, 1, 2, 3],
    [0, 4, 1, 3],
    [0, 3, 1, 2, 4],
    [0, 1, 2, 3, 4],
    [0, 1, 3, 4],
    [0, 3, 1, 4],
    [3, 1, 4, 0],
    [0, 4, 3, 1, 2],
    [0, 4, 2, 3, 1],
]

# ═══════════════════════════════════════════════════════════════════
#  POST BUILD CONSTANTS — captured from live client (M3 values)
# ═══════════════════════════════════════════════════════════════════
# উপরে
HELLX_vERS = "2.132.8"

FIXED_MIDDLE = bytes.fromhex(
    "010102010104424400020300010000040e322e3133322e381432303139313138353235"
    "ca0163736f7665727365612e7374726f6e67686f6c642e66726565666972656d6f6269"
    "6c652e636f6d3b302e302e302e303b33342e3132362e37362e34353b33342e38372e31"
    "37372e31343b33342e38372e3137302e3233303b33352e3138352e3138332e353700"
)
assert len(FIXED_MIDDLE) == 139

DEFAULT_MID = bytes.fromhex("0000000000000000000100000000000100000000010100c8ddf58daae58cdf110200")
DEFAULT_HEX_PART = b"5cd9b3f05ab07bca7bf41f68ad93e21ee17b2c8f8e00e752ce906d9910e8a545"

# Regex / debug
def _hexdump(data, indent="      ", width=16):
    return "\n".join(
        f"{indent}{i:04X}  " + " ".join(f"{b:02X}" for b in data[i:i+width]) +
        "  " + "".join(chr(b) if 32 <= b < 127 else "." for b in data[i:i+width])
        for i in range(0, len(data), width))

async def parse_layout(layout):
    if isinstance(layout, str):
        return [int(c) for c in layout.strip()]
    if isinstance(layout, int):
        return [int(c) for c in str(layout)]
    return list(layout)

async def build_padded(content):
    pad_len = (8 - (len(content) + 10) % 8) % 8
    return bytes([pad_len, 0, 0]) + b"\x00" * pad_len + content + b"\x00" * 7

async def tea_enc(v0, v1, k0, k1, k2, k3):
    s = 0
    for _ in range(_ROUNDS):
        s = (s + _DELTA) & 0xFFFFFFFF
        v0 = (v0 + (((((v1 << 4) & 0xFFFFFFFF) + k0) & 0xFFFFFFFF) ^
                     ((v1 + s) & 0xFFFFFFFF) ^
                     ((((v1 >> 5) + k1) & 0xFFFFFFFF)))) & 0xFFFFFFFF
        v1 = (v1 + (((((v0 << 4) & 0xFFFFFFFF) + k2) & 0xFFFFFFFF) ^
                     ((v0 + s) & 0xFFFFFFFF) ^
                     ((((v0 >> 5) + k3) & 0xFFFFFFFF)))) & 0xFFFFFFFF
    return v0, v1

async def tea_cbc_encrypt(padded, key_bytes):
    k0, k1, k2, k3 = struct.unpack_from("<IIII", key_bytes, 0)
    out = bytearray(len(padded))
    pc = bytearray(8)
    pi = bytearray(8)
    for i in range(0, len(padded), 8):
        x = bytearray(8)
        for j in range(8):
            x[j] = padded[i + j] ^ pc[j]
        e0, e1 = await tea_enc(
            struct.unpack_from("<I", x, 0)[0],
            struct.unpack_from("<I", x, 4)[0],
            k0, k1, k2, k3
        )
        enc = bytearray(8)
        struct.pack_into("<I", enc, 0, e0)
        struct.pack_into("<I", enc, 4, e1)
        for j in range(8):
            out[i + j] = enc[j] ^ pi[j]
        pc[:] = out[i:i + 8]
        pi[:] = x
    return bytes(out)

async def encode_header(layout, send_opt, cmd, order_id, flags, length, k, v80):
    out = bytearray()
    for code in layout:
        val = {0: send_opt, 1: cmd, 2: order_id, 3: flags, 4: length}[code]
        if _FIELD_SIZES[code] == 1:
            out.append((val & 0xFF) ^ k)
        else:
            v = ((val & 0xFFFF) ^ v80) & 0xFFFF
            out.append(v & 0xFF)
            out.append((v >> 8) & 0xFF)
    return bytes(out)

async def crc7_buff(crc, buf):
    c = crc & 0x7F
    for b in buf:
        c = CRC7_TABLE[((2 * (c & 0xFF)) ^ (b & 0xFF)) & 0xFF] & 0x7F
    return c & 0x7F

def _crc7(buf):
    c = 0
    for b in buf:
        c = CRC7_TABLE[((2 * c) ^ b) & 0xFF] & 0x7F
    return c

async def has_ssan_zig(n):
    z = (n << 1) & 0xFFFFFFFFFFFFFFFF
    out = bytearray()
    while z >= 0x80:
        out.append((z & 0x7F) | 0x80)
        z >>= 7
    out.append(z)
    return bytes(out)

async def uleb_encode(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            b |= 0x80
        out.append(b)
        if not n:
            break
    return bytes(out)

async def sv_frame(msg_key, layout, send_option, cmd, order_id, flags, content, key, encrypted=True):
    k = key[0]
    v80 = ((k << 8) | k) & 0xFFFF
    body = await tea_cbc_encrypt(await build_padded(content), key) if encrypted else content
    hdr = bytearray([msg_key, 0]) + await encode_header(
        layout, send_option, cmd, order_id, flags, len(body), k, v80
    )
    packet = bytearray(hdr + body)
    packet[1] = await crc7_buff(0, bytes(packet[2:])) & 0x7F
    return bytes(packet)

def _decode_response(data: bytes, preferred_layouts=None):
    if len(data) < 4:
        return None

    crc_ok = (data[1] & 0x7F) == _crc7(data[2:])
    best = None

    layouts = preferred_layouts if preferred_layouts else RESPONSE_LAYOUTS

    for k in range(256):
        v80 = ((k << 8) | k) & 0xFFFF
        for layout in layouts:
            off = 2
            hdr = {}
            ok = True
            for code in layout:
                sz = _FIELD_SIZES[code]
                if off + sz > len(data):
                    ok = False
                    break
                if sz == 1:
                    hdr[_FIELD_NAMES[code]] = data[off] ^ k
                    off += 1
                else:
                    val = data[off] | (data[off + 1] << 8)
                    hdr[_FIELD_NAMES[code]] = val ^ v80
                    off += 2
            if not ok:
                continue
            if hdr.get("sendOption", 0) > 7:
                continue
            if hdr.get("flags", 0) > 7:
                continue
            if hdr.get("length", 0) != len(data) - off:
                continue

            cmd = hdr.get("cmd", 0)
            score = 0
            if cmd in MESSAGE_ID_TO_NAME:
                score += 20                      # known cmd — highest weight
            # prefer sendOption==0 (server responses usually start with 0)
            if hdr.get("sendOption") == 0:
                score += 10
            # prefer flags==1 (encrypted) or flags==0
            if hdr.get("flags") in (0, 1):
                score += 3
            score += len(layout)
            if crc_ok:
                score += 5

            cand = {
                "k": k,
                "layout": layout,
                "sendOption": hdr.get("sendOption"),
                "cmd": cmd,
                "flags": hdr.get("flags"),
                "orderId": hdr.get("orderId"),
                "length": hdr.get("length"),
                "body_off": off,
                "crc_ok": crc_ok,
                "_score": score,
            }
            if best is None or cand["_score"] > best["_score"]:
                best = cand

    return best

def _decode_request(data: bytes, udp_key_b: bytes, layout_list: list):
    if not data or len(data) < 4 or not udp_key_b:
        return None

    k = udp_key_b[0]
    v80 = ((k << 8) | k) & 0xFFFF
    crc_ok = (data[1] & 0x7F) == _crc7(data[2:])

    off = 2
    hdr = {}
    for code in layout_list:
        sz = _FIELD_SIZES[code]
        if off + sz > len(data):
            return None
        if sz == 1:
            hdr[_FIELD_NAMES[code]] = data[off] ^ k
            off += 1
        else:
            val = data[off] | (data[off + 1] << 8)
            hdr[_FIELD_NAMES[code]] = val ^ v80
            off += 2

    return {
        "k": k,
        "layout": layout_list,
        "sendOption": hdr.get("sendOption"),
        "cmd": hdr.get("cmd"),
        "flags": hdr.get("flags"),
        "orderId": hdr.get("orderId"),
        "length": hdr.get("length"),
        "body_off": off,
        "crc_ok": crc_ok,
    }

async def build_packet(msg_key, layout, send_option, cmd, order_id, flags, content, key, encrypted=True):

    k = key[0]
    v80 = ((k << 8) | k) & 0xFFFF

    # ── body: encrypt if needed ──
    if encrypted:
        padded = await build_padded(content)
        body = await tea_cbc_encrypt(padded, key)
    else:
        body = content

    # ── header ──
    hdr = bytearray([msg_key, 0x00])
    for code in layout:
        value = {0: send_option, 1: cmd, 2: order_id, 3: flags, 4: len(body)}[code]
        if _FIELD_SIZES[code] == 1:
            hdr.append((value & 0xFF) ^ k)
        else:
            v = ((value & 0xFFFF) ^ v80) & 0xFFFF
            hdr.append(v & 0xFF)
            hdr.append((v >> 8) & 0xFF)

    # ── assemble ──
    packet = bytearray(hdr + body)
    packet[1] = await crc7_buff(0, bytes(packet[2:])) & 0x7F
    return bytes(packet)

async def build_hello_packet(account_id, key, layout):
    suffix  = "4239"       # 4-digit client-chosen suffix
    msg_key = 0x62         # client-chosen msg_key

    layout_list = await parse_layout(layout)
    k = key[0]
    v80 = ((k << 8) | k) & 0xFFFF

    # Content: [uint32_le(len)] + [text] + [9×0x00]
    text = f"{account_id}_{suffix}"
    tb   = text.encode("utf-8")
    content = struct.pack("<I", len(tb)) + tb + b"\x00" * 9

    # Padded + TEA-CBC encrypt
    padded = await build_padded(content)
    body   = await tea_cbc_encrypt(padded, key)

    # Header: send=1, cmd=1, order=0, flags=1, length=len(body)
    hdr = await encode_header(layout_list, 1, 1, 0, 1, len(body), k, v80)

    # Assemble
    packet = bytearray([msg_key, 0x00]) + hdr + body
    packet[1] = await crc7_buff(0, bytes(packet[2:])) & 0x7F

    print(f"[HELLO] text='{text}' body={len(body)} total={len(packet)} crc=0x{packet[1]:02x}")
    return bytes(packet).hex()

# ═══════════════════════════════════════════════════════════════════
#  PREPARE + POST builders
# ═══════════════════════════════════════════════════════════════════
async def build_prepare_packet(account_id, block_val, udp_key, layout, jwt_token, jwt_len=660):
    """
    Build RUDP_JOIN_MATCH_PREPARE (cmd=447).
    Content = has_ssan_zig(jwt_len) + jwt[:jwt_len]
    """
    jwt_part = jwt_token[:jwt_len].encode() if jwt_token else b""
    content = (await has_ssan_zig(len(jwt_part))) + jwt_part
    pkt = await build_packet(0x63, layout, 2, 447, 0, 1, content, udp_key)
    return pkt


async def build_post_packet(account_id, block_val, host, jwt_token, udp_key, layout,
                            name=b"", mid=None, hex_part=None, msg_key=0x5A):
    """
    RUDP_JOIN_MATCH_POST (cmd=448) — real CS structure.
      • const 15/1 (not 43/11)
      • host = real server_addr
      • sig_len = uleb_encode(len(jwt_sig) * 2)
      • rand5 = fixed (server ignores)
      • hex_part = 32 raw bytes
    """
    if mid is None:      mid = DEFAULT_MID
    if hex_part is None: hex_part = DEFAULT_HEX_PART

    c = bytearray()

    # 6 uleb varints — FIXED: 43→15, 11→1
    c += await uleb_encode(account_id)
    c += await uleb_encode(block_val)
    c += await uleb_encode(1)
    c += await uleb_encode(15)               # ★ was 43
    c += await uleb_encode(block_val)
    c += await uleb_encode(1)                # ★ was 11

    # 6 zeros + FIXED_MIDDLE
    c += b"\x00" * 6
    c += FIXED_MIDDLE

    # ── TAIL ──
    c += b"\x00\x00\x00"                     # prefix3
    c += b"\x00\x00\x01\x00\x00"             # rand5 (fixed — server ignores)
    c += bytes([len(name) * 2])              # name_len × 2
    c += name
    c += mid

    # ★ HOST — real server_addr
    host_b = host.encode()
    c += bytes([len(host_b) * 2])
    c += host_b

    c += b"\x80\x01"                         # marker
    c += hex_part                            # 32 raw bytes

    # ★ jwt_sig + sig_len as ULEB varint (NOT 2-byte LE!)
    jwt_parts = jwt_token.split(".")
    if len(jwt_parts) >= 3:
        payload_b64 = jwt_parts[1]
        sig         = jwt_parts[2]
        K = len(payload_b64) - 623
        if K <= 0 or K > len(payload_b64):
            K = 204
        jwt_sig = (payload_b64[-K:] + "." + sig).encode()
        sig_len_x2 = len(jwt_sig) * 2
        c += await uleb_encode(sig_len_x2)   # ★ uleb, not struct.pack
        c += jwt_sig

    content = bytes(c)
    pkt = await build_packet(msg_key, layout, 2, 448, 1, 1, content, udp_key)
    return pkt, content

async def _keepalive_ping(sock, ip, port, udp_key_b, layout_nr, stop_event):
    """
    Send PING (cmd=3, flags=0) every 1 second to keep UDP match alive.
    Rotates through multiple msg_keys like the real client.
    """
    ping_keys = [0x66, 0x6D, 0x69, 0x6C, 0x6B, 0x6E, 0x6F, 0x70]
    loop = asyncio.get_event_loop()
    i = 0
    k = udp_key_b[0]; v80 = ((k << 8) | k) & 0xFFFF

    while not stop_event.is_set():
        pk = ping_keys[i % len(ping_keys)]
        counter = int(time.time() * 1000) & 0xFFFFFFFF
        content = struct.pack("<I", counter) + b"\x00\x00\x00"
        hdr = await encode_header(layout_nr, 0, 3, 0, 0, len(content), k, v80)
        pkt = bytearray([pk, 0x00]) + hdr + content
        pkt[1] = await crc7_buff(0, bytes(pkt[2:])) & 0x7F
        try:
            await loop.sock_sendto(sock, bytes(pkt), (ip, port))
            print(f"{Style.BRIGHT}{Fore.CYAN}[KEEPALIVE] PING 0x{pk:02X}  counter={counter}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Style.BRIGHT}{Fore.RED}[KEEPALIVE ERROR] {e}{Style.RESET_ALL}")
            break
        i += 1
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=1.0)
        except asyncio.TimeoutError:
            pass

# ═══════════════════════════════════════════════════════════════════
#  Periodic senders (start after JOIN_MATCH confirmation)
# ═══════════════════════════════════════════════════════════════════
# 1) SYNC_SERVER_TIME (cmd=2000) — every 1 second
_SYNC_TIME_MSG_KEYS = [0x65, 0x64, 0x68, 0x69, 0x6D, 0x6A]
_SYNC_TIME_INITIAL  = 120
_SYNC_TIME_STEP     = 60
_SYNC_TIME_INTERVAL = 1.0

# 2) UDP_ACK (cmd=2) — every 1 second
_ACK_INTERVAL     = 1.0
_ACK_LAYOUT       = [0, 4, 1, 3]
_ACK_MSG_KEYS     = [0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x6B, 0x6C, 0x6D]
_ACK_COUNTER_BASE = 35

# 3) PLAYER_STATE_SYNC (cmd=2001) — every 10 seconds
_TEST_UDP_INTERVAL = 10.0
_TEST_UDP_LAYOUT   = [0, 3, 4, 1]
_TEST_UDP_MSG_KEY  = 0x68
_TEST_UDP_BODY     = bytes.fromhex(
    "81808008B89313D002D5CD11BC010046"
    "00000000000000"
    "CDD1BFFB0300"
    "EECFCAF5030000"
    "B6060000008459"
)
assert len(_TEST_UDP_BODY) == 43

# 4) Emote (cmd=371) — every 10 seconds (replay captured)
_TEST_EMOTE_INTERVAL = 10.0
_TEST_EMOTE_HEX = (
    "627f5e7c5c2f5d5d4a5ca702915ba0daf58892b6350a2815b9cf9c5c310a9e97"
    "a233305a4481391718dd"
)

# ═══════════════════════════════════════════════════════════════════
#  Background task 1: SYNC_SERVER_TIME (cmd=2000, 1s)
# ═══════════════════════════════════════════════════════════════════
async def _sync_time_sender(sock, ip, port, udp_key_b, layout_nr, stop_event,
                             interval=_SYNC_TIME_INTERVAL):
    loop = asyncio.get_event_loop()
    k = udp_key_b[0]; v80 = ((k << 8) | k) & 0xFFFF
    counter = _SYNC_TIME_INITIAL
    i = 0
    while not stop_event.is_set():
        try:
            counter += _SYNC_TIME_STEP
            mk = _SYNC_TIME_MSG_KEYS[i % len(_SYNC_TIME_MSG_KEYS)]
            content = await uleb_encode(counter)
            hdr = await encode_header(layout_nr, 0, 2000, 0, 0, len(content), k, v80)
            pkt = bytearray([mk, 0x00]) + hdr + content
            pkt[1] = await crc7_buff(0, bytes(pkt[2:])) & 0x7F
            await loop.sock_sendto(sock, bytes(pkt), (ip, port))
            print(f"{Style.BRIGHT}{Fore.CYAN}[SYNC_TIME] sent 0x{mk:02X}  "
                  f"counter={counter}  ({len(pkt)}B){Style.RESET_ALL}")
        except Exception as e:
            print(f"{Style.BRIGHT}{Fore.RED}[SYNC_TIME ERROR] {e}{Style.RESET_ALL}")
            break
        i += 1
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            pass


# ═══════════════════════════════════════════════════════════════════
#  Background task 2: UDP_ACK (cmd=2, 1s)
# ═══════════════════════════════════════════════════════════════════
async def _ack_sender(sock, ip, port, udp_key_b, layout_nr, stop_event,
                      counter_holder, interval=_ACK_INTERVAL):
    loop = asyncio.get_event_loop()
    k = udp_key_b[0]; v80 = ((k << 8) | k) & 0xFFFF
    i = 0
    while not stop_event.is_set():
        try:
            counter_holder[0] = (counter_holder[0] + 1) & 0xFFFF
            counter = counter_holder[0]
            mk = _ACK_MSG_KEYS[i % len(_ACK_MSG_KEYS)]
            content = struct.pack("<H", counter)
            padded  = await build_padded(content)
            body    = await tea_cbc_encrypt(padded, udp_key_b)
            hdr = await encode_header(layout_nr, 0, 2, 0, 1, len(body), k, v80)
            pkt = bytearray([mk, 0x00]) + hdr + body
            pkt[1] = await crc7_buff(0, bytes(pkt[2:])) & 0x7F
            await loop.sock_sendto(sock, bytes(pkt), (ip, port))
            print(f"{Style.BRIGHT}{Fore.GREEN}[ACK] sent 0x{mk:02X}  "
                  f"counter={counter}  ({len(pkt)}B){Style.RESET_ALL}")
        except Exception as e:
            print(f"{Style.BRIGHT}{Fore.RED}[ACK SENDER ERROR] {e}{Style.RESET_ALL}")
            break
        i += 1
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            pass


# ═══════════════════════════════════════════════════════════════════
#  Background task 3: PLAYER_STATE_SYNC (cmd=2001, 10s)
# ═══════════════════════════════════════════════════════════════════
async def _state_sync_sender(sock, ip, port, udp_key_b, stop_event,
                              interval=_TEST_UDP_INTERVAL):
    loop = asyncio.get_event_loop()
    k = udp_key_b[0]; v80 = ((k << 8) | k) & 0xFFFF
    body = _TEST_UDP_BODY
    count = 0
    try:
        await asyncio.wait_for(stop_event.wait(), timeout=interval)
    except asyncio.TimeoutError:
        pass
    while not stop_event.is_set():
        try:
            count += 1
            hdr = await encode_header(_TEST_UDP_LAYOUT, 0, 2001, 0, 0, len(body), k, v80)
            pkt = bytearray([_TEST_UDP_MSG_KEY, 0x00]) + hdr + body
            pkt[1] = await crc7_buff(0, bytes(pkt[2:])) & 0x7F
            await loop.sock_sendto(sock, bytes(pkt), (ip, port))
            print(f"{Style.BRIGHT}{Fore.MAGENTA}[STATE_SYNC] sent #{count}  "
                  f"cmd=2001  ({len(pkt)}B){Style.RESET_ALL}")
        except Exception as e:
            print(f"{Style.BRIGHT}{Fore.RED}[STATE_SYNC ERROR] {e}{Style.RESET_ALL}")
            break
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            pass


# ═══════════════════════════════════════════════════════════════════
#  Background task 4: Emote replay (cmd=371, 10s)
# ═══════════════════════════════════════════════════════════════════
async def _emote_sender(sock, ip, port, stop_event, interval=_TEST_EMOTE_INTERVAL):
    loop = asyncio.get_event_loop()
    pkt_bytes = bytes.fromhex(_TEST_EMOTE_HEX)
    count = 0
    try:
        await asyncio.wait_for(stop_event.wait(), timeout=interval)
    except asyncio.TimeoutError:
        pass
    while not stop_event.is_set():
        try:
            count += 1
            await loop.sock_sendto(sock, pkt_bytes, (ip, port))
            print(f"{Style.BRIGHT}{Fore.YELLOW}[EMOTE] sent #{count}  "
                  f"cmd=371  ({len(pkt_bytes)}B){Style.RESET_ALL}")
        except Exception as e:
            print(f"{Style.BRIGHT}{Fore.RED}[EMOTE ERROR] {e}{Style.RESET_ALL}")
            break
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            pass

def cs_match_start_packet(key, iv):
    fields = {
        1: 1,
        2: {
            1: bytes.fromhex("01"),
            2: 15,
            7: {
                1: "IDC1",
                2: 18446744073709552000,
                3: "BD"
            },
            8: 1,
            9: bytes.fromhex("01090a0b1219202729"),
            11: 1,
            12: {
                1: bytes.fromhex(
                    "088B823F43C756100201010000000000001600020014000268C342040F0000004676"
                    "2514110000017a17084b0e748c3f6aa0546d000000ff00000100cacfa16d"
                ),
                2: 60,
                3: bytes.fromhex(
                    "745e58551400034453530d565356040e06065c520e0f560557560f010a590152580a"
                    "510d5353570b1b000645775a44444e190314001e1a03054800517f710b5e6f486878"
                    "7e624e47716e5f7e7d04710c657c037a750c14084e62045a6156556867537e076e6e"
                    "027f477a4d7e024d745c6553747c0e1b575857461867781a764348004b6e60604400"
                    "444556425d426e194d7c4840086a77795c4c601842080a12020b4d7f53600f584544"
                    "545c5d4b0f72540460030e55650e73067f0743000d14094f4c0667165964661f6d08"
                    "774b6b5d4a59457d5b4e1a7d135e4f4a730a17024b6b777601666b615601617f6861"
                    "6f50634a474500710041584b504004110e4856005b670876555a464e7c060f49540a"
                    "5a5454645a5a716f06425f0c14080a4b446278074b6f65756a06531f4861604b4b46"
                    "7b606a5562416e7a5c051204455c7e7a4a071e497f567f5274637c76447371084259"
                    "7b0a785104540c100c4d5a494a7d4d56417d6b75785151516d6e664457616d760748"
                    "505b530d14030344526d4160074d604d5e7f17616d5b637c766460405670624e4103"
                    "6e0913024d6b567a654b730756097a7551137f794c7f4d61031c64617c5a56090f14"
                    "034c665a65497d1800737a50061c095d7c59767c7c444e476f530b4e5a0a1a044b7a"
                    "09795b525c627d6942450168477a050072510d73700c7c6e660b05"
                ),
                4: "y^]]",
                6: 14,
                7: bytes.fromhex("1d01726e517970171c"),
                8: str(HELLX_vERS),
                9: 2,
                10: 1,
                11: bytes.fromhex(
                    "036262535136336a7278394d52416456324b796f566c513941374435764b446e334b"
                    "66384d667670456d6e4f774d51536b3230722f3237347134382b4451516d626f3679"
                    "4458636a6a7139434877304b306e7843635761744b6d504d4a396353766d776c2f4a"
                    "5a2b6c3773415a373253705446393263646d45754e537068395343426d694f6c3775"
                    "6142645168486b6242397a2b494f366950314d39506c5135746e5a79725166796f59"
                    "7a6b4f38644c664f6a474841464d7665623345594b3871707a615179644753564867"
                    "44626e56493353596d4b372f4b6d49674655514e48306e5472766e65346764734370"
                    "75762f464a4749375742562b526365766b373077447877466e734478317179376d73"
                    "76362f6e5a62794a506c5a2b344e4d4d3247397650462b566d2f35674269396e3162"
                    "62635a762f3974334277746f63645a755861676c6a5261793275344c634350523671"
                    "734b6c64436739346b756a5243316c6f4650705069334b4d52685039616b43316d75"
                    "46722b2f374d6455525848356f4d654e54534a6d63316a49464d4a49676f31484b64"
                    "454b596a6b695433544b50617831763878426a38644d582b524844566e507144316b"
                    "466756775a6752495035617153584139333731436678465a424a36734a35674a7057"
                    "61696a596f744e503352514b4352357557654f776f78574d77706472722f74437562"
                    "53524472544a586957506f4675724a6d443734746c7a7677384274355976436c772b"
                    "47686c636c5156517657545778507363746e73375049675752774d754f652b754674"
                    "2f7962374c772b675847426972466f4e4c72424a37774b3868302b535a756b435041"
                    "506f5a77492b61567a6e476434586d7a7a30734a34644845616c7446724f66546458"
                    "37553d"
                )
            },
            20: {1: 21},
            21: "a_6534489873065906362"
        }
    }
    proto = create_proto(fields).hex()
    return create_packet(proto, '0319', key, iv)

def reject_invite(uid, name_text, key, iv):
    fields = {
        1: 5,
        2: {
            1: int(uid),
            2: 1,
            3: int(uid),
            4: str(name_text)
        }
    }
    
    proto = create_proto(fields).hex()
    packet_type = '0515'
    packet = create_packet(proto, packet_type, key, iv)
    
    return packet

def accept_invite(uid, group_id, key, iv):
    fields = {
        1: 4,
        2: {
            1: int(uid),
            3: int(uid),
            4: bytes.fromhex("0107090a0b120f19202729"),
            8: 1,
            9: {
                1: "08FBA33B0522052002041B0222220007000C00010004000547E265AE1080779546762514110104076fa2e8770e748c3f6a68ed75000000ff08080500cacfa16d",
                2: 235,
                3: {
                    14: 80,
                    11: 86
                },
                4: "{Y\\R",
                6: 13,
                7: {2: 4},
                8: f"{game_version}",
                9: 2,
                10: 1,
                11: "0362625351363749545a306f50416456324b796f566c664b314a522b4c336737676d2f597a6f7064736278516b676d6f3275696a4e5a512f6445356778643942356c6f69644867315574306e34573146634c382b624a69436c61532b305a625070547a32574f302b436d497067325958347a4d38722f526a4a735371764a334a357a69756950676b5a35642b386a7576664367547a7135776e78756b4d5a734d63745544582b666a65325373565833542b6950676c4f31474736526e66383661754e7945786c4a6942316a656d59636452595459496c65612f68757353657a6c6753424c49714e64482f584b7876507a6c74417461756b53746d50414b4c5679544b42337536685146456b7635584962534f626f6f436b4b357a614e523736746e6e6b576176776748446e73426770656c75506e6652644e75714c43547a5553707569355a77425448653937667465354c3432365a71554441724933565a3636687030546234384c756730562b366c514d66636e467143486d33436a356f5549395369776934424758454e33317436786c794932416f6b2f4a322f2b355255574d3645774c497338306a632f55317765745a6b457639524e496f70563275726d38324e4a4858757166346e4d45785a516e6879766268334e5a68554a3431427934574a4b6f44656d367864733873474e444e5874472b4a68466976714d683235536139744b354462336f416871463769416675472f336535304e44744e4e3643796a794a5370633334784765696f6165533544597663782b77634c656e4c373945517475547477716d7a4b4d7575536268514635785272717978796538452f7a5563706a7739534d58654b5268394b685252666b6f4f51785741673d3d"
            },
            10: str(group_id),
            11: {
                1: "IDC3",
                2: 107,
                3: "BD"
            },
            13: "en",
            16: "374f5219",
            20: {1: 21},
            23: "a_6534489873065906362",
            24: "https://dl-sg-production.freefiremobile.com/D5A73B5E05EC88BB7181_7104104913_107_1767710870_0",
            27: {1: 2, 2: 4}
        }
    }
    
    proto = create_proto(fields).hex()
    packet_type = '0515'
    packet = create_packet(proto, packet_type, key, iv)
    
    return packet

def accept_join_request(account_id, target_uid, key, iv):
    fields = {
        1: 38,
        2: {
            1: int(account_id),
            2: int(target_uid),
            8: 1
        }
    }
    
    proto = create_proto(fields).hex()
    packet_type = '0515'
    packet = create_packet(proto, packet_type, key, iv)
    
    return packet

def accept_room_join(uid, key, iv):
    fields = {
        1: 22,
        2: {
            1: int(uid),
            2: 1
        }
    }
    
    proto = create_proto(fields).hex()
    packet_type = '0E15'
    packet = create_packet(proto, packet_type, key, iv)
    
    return packet

def accept_room_invite_or_join_room(room_id, room_password, key, iv):
    fields = {
        1: 3,
        2: {
            1: int(room_id),
            2: str(room_password) if room_password else None,
            8: {
                1: "IDC3",
                2: 142,
                3: "BD"
            },
            9: bytes.fromhex("0107090a0b120f19202729"),
            10: 1,
            12: bytes.fromhex("ffffffffffffffffff01ffffffffffffffffff01"),
            13: 1,
            14: 1,
            16: "en",
            22: {1: 21},
            24: 1,
            25: "a_6534489873065906362"
        }
    }
    
    proto = create_proto(fields).hex()
    packet_type = '0E15'
    packet = create_packet(proto, packet_type, key, iv)
    
    return packet

def join_ghost(player_id, secret_code, name, key, iv):
    fields = {
        1: 61,
        2: {
            1: int(player_id),
            2: {
                1: int(player_id),
                2: int(account_id),
                3: str(name),
                5: 1787866961,
                6: 53,
                7: 25,
                8: {2: 1, 3: 1},
                9: 12,
            },
            3: str(secret_code),
        },
    }
    
    proto = create_proto(fields).hex()
    packet_type = '0515'
    packet = create_packet(proto, packet_type, key, iv)
    
    return packet

def auth_team_chat(owner_uid, chat_code, key, iv):
    fields = {
        1: 3,
        2: {
            1: owner_uid,
            3: "en",
            4: str(chat_code)
        }
    }
    
    proto = create_proto(fields).hex()
    packet_type = '1215'
    packet = create_packet(proto, packet_type, key, iv)
    
    return packet

def auth_room_chat(room_id, chat_code, key, iv):
    fields = {
        1: 3,
        2: {
            1: int(room_id),
            2: 3,
            3: "en",
            4: str(chat_code)
        }
    }
    
    proto = create_proto(fields).hex()
    packet_type = '1215'
    packet = create_packet(proto, packet_type, key, iv)
    
    return packet

def auth_clan_chat(clan_id, clan_key, key, iv):
    fields = {
        1: 3,
        2: {
            1: int(clan_id),
            2: 1,
            4: str(clan_key)
        }
    }
    
    proto = create_proto(fields).hex()
    packet_type = '1201'
    packet = create_packet(proto, packet_type, key, iv)
    
    return packet

def auth_global_chat(chat_type, key, iv):
    fields = {
        1: 3,
        2: {
            2: chat_type,
            3: "en"
        }
    }
    
    proto = create_proto(fields).hex()
    packet_type = '1215'
    packet = create_packet(proto, packet_type, key, iv)
    
    return packet

def auth_social_island_chat(chat_code, key, iv):
    fields = {
        1: 3,
        2: {
            1: chat_code,
            2: 10,
            3: "en"
        }
    }
    
    proto = create_proto(fields).hex()
    packet_type = '1219'
    packet = create_packet(proto, packet_type, key, iv)
    
    return packet

def status_packet(uid, key, iv):
    uid_enc = hex(int(uid))[2:]
    if len(uid_enc) % 2 != 0:
        uid_enc = '0' + uid_enc
    
    fields = {
        1: 1,
        2: {
            1: int(uid),
            2: 5
        }
    }
    
    proto = create_proto(fields).hex()
    packet_type = '0F15'
    packet = create_packet(proto, packet_type, key, iv)
    
    return packet

def send_message(uid, chat_id, chat_type, message, key, iv):
    fields = {
        1: int(uid),
        2: int(chat_id),
        3: chat_type,
        4: message,
        5: int(datetime.now().timestamp()),
        9: {
            1: "efbc97efbcb8e38080efbcadefbca1efbcb2efbcb5efbca6",
            2: 902037031,
            3: 901037021,
            4: 312,
            5: 827001005,
            8: "7X~ARMY",
            10: 1,
            11: 7,
            13: {1: 2},
            14: {
                1: int(uid),
                2: 8,
                3: b"\x01\x06\x02"
            },
            18: {
                1: int(uid),
                3: 6,
                4: ""
            }
        },
        10: "en",
        13: {
            1: "https://lh3.googleusercontent.com/a/ACg8ocKUtmlPUNJL7Tk9jW7Unh4Y1UGAPQcVWEV9mxVsPibjK-9ngw=s96-c",
            2: 1,
            3: 1
        },
        14: {
            1: {
                1: 1,
                2: 4,
                3: 15,
                4: 1,
                5: 1789326000,
                6: "BD"
            }
        }
    }

    proto = create_proto(fields).hex()
    proto = "080112" + encrypt_chat_packet(len(proto) // 2, Tp='Uid') + proto
    packet_type = '1201'
    packet = create_packet(proto, packet_type, key, iv)

    return packet

def send_json(uid, chat_id, chat_type, json, key, iv):
    if "StickerStr" in json or "TitleID" in json:
        show_type = 0
    else:
        show_type = 1

    fields = {
        1: int(uid),
        2: int(chat_id),
        3: chat_type,
        5: int(datetime.now().timestamp()),
        7: show_type,
        8: json,
        9: {
            1: "efbc97efbcb8e38080efbcadefbca1efbcb2efbcb5efbca6",
            2: 902037031,
            3: 901037021,
            4: 312,
            5: 827001005,
            8: "7X~ARMY",
            10: 1,
            11: 7,
            13: {1: 2},
            14: {
                1: int(uid),
                2: 8,
                3: b"\x01\x06\x02"
            },
            18: {
                1: int(uid),
                3: 6,
                4: ""
            }
        },
        10: "en",
        13: {
            1: "https://lh3.googleusercontent.com/a/ACg8ocKUtmlPUNJL7Tk9jW7Unh4Y1UGAPQcVWEV9mxVsPibjK-9ngw=s96-c",
            2: 1,
            3: 1
        },
        14: {
            1: {
                1: 1,
                2: 4,
                3: 15,
                4: 1,
                5: 1789326000,
                6: "BD"
            }
        }
    }

    proto = create_proto(fields).hex()
    proto = "080112" + encrypt_chat_packet(len(proto) // 2, Tp='Uid') + proto
    packet_type = '1201'
    packet = create_packet(proto, packet_type, key, iv)

    return packet

def fix_num(number):
    return '[c]'.join(str(number)[i:i+3] for i in range(0, len(str(number)), 3))

def encrypt_chat_packet(H , Tp):
    e , H = [] , int(H)
    while H:
        e.append((H & 0x7F) | (0x80 if H > 0x7F else 0)) ; H >>= 7
    return bytes(e).hex() if Tp == 'Uid' else None

def encrypt_aes(hex_data):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(bytes.fromhex(hex_data), AES.block_size)).hex()

def create_vr(N):
    if N < 0:
        return b''
    H = []
    while True:
        S = N & 0x7F
        N >>= 7
        if N:
            S |= 0x80
        H.append(S)
        if not N:
            break
    return bytes(H)

def create_variant(field_number, value):
    field_header = (field_number << 3) | 0
    return create_vr(field_header) + create_vr(value)

def create_length(field_number, value):
    field_header = (field_number << 3) | 2
    encoded_value = value.encode() if isinstance(value, str) else value
    return create_vr(field_header) + create_vr(len(encoded_value)) + encoded_value

def create_proto(fields):
    try:
        packet = bytearray()
        for field, value in fields.items():
            if isinstance(field, str):
                field = int(field)
            if isinstance(value, dict):
                nested_packet = create_proto(value)
                packet.extend(create_length(field, nested_packet))
            elif isinstance(value, int):
                packet.extend(create_variant(field, value))
            elif isinstance(value, str) or isinstance(value, bytes):
                packet.extend(create_length(field, value))
        return packet
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[CREATE PROTO ERROR] {e}")
        return None

def decode_varint(data, offset):
    result = 0
    shift = 0
    while offset < len(data):
        byte = data[offset]
        result |= (byte & 0x7F) << shift
        offset += 1
        if not (byte & 0x80):
            return result, offset
        shift += 7
    return None, offset

def decode_protobuf(data):
    result = {}
    offset = 0
    data_len = len(data)
    while offset < data_len:
        header, offset = decode_varint(data, offset)
        if header is None:
            break
        field_number = header >> 3
        wire_type = header & 0x7
        if wire_type == 0:
            value, offset = decode_varint(data, offset)
            if value is not None:
                result[field_number] = value
        elif wire_type == 2:
            length, offset = decode_varint(data, offset)
            if length is None:
                break
            value = data[offset:offset + length]
            offset += length
            try:
                result[field_number] = value.decode('utf-8')
            except:
                result[field_number] = value.hex()
        elif wire_type == 1:
            offset += 8
        elif wire_type == 3:
            offset += 4
        else:
            break
    return result

def decode_protobuf_2(data):
    result = {}
    offset = 0
    data_len = len(data)
    
    while offset < data_len:
        header, offset = decode_varint(data, offset)
        if header is None:
            break
        
        field_number = header >> 3
        wire_type = header & 0x7
        
        if wire_type == 0:
            value, offset = decode_varint(data, offset)
            if value is not None:
                result[field_number] = value
                
        elif wire_type == 2:
            length, offset = decode_varint(data, offset)
            if length is None:
                break
            value = data[offset:offset + length]
            offset += length
            
            try:
                decoded_str = value.decode('utf-8')
                if decoded_str and len(decoded_str) > 0:

                    if len(decoded_str) > 10 and all(c in '0123456789abcdef' for c in decoded_str.lower()):
                        try:
                            hex_decoded = bytes.fromhex(decoded_str).decode('utf-8', errors='ignore')
                            if hex_decoded and len(hex_decoded) > 0:
                                result[field_number] = hex_decoded
                            else:
                                result[field_number] = decoded_str
                        except:
                            result[field_number] = decoded_str
                    else:
                        result[field_number] = decoded_str
                else:

                    nested = decode_protobuf(value)
                    if nested:
                        result[field_number] = nested
                    else:
                        result[field_number] = value.hex()
            except UnicodeDecodeError:

                nested = decode_protobuf(value)
                if nested:
                    result[field_number] = nested
                else:

                    result[field_number] = value.hex()
                
        elif wire_type == 1:
            offset += 8
        elif wire_type == 3:
            offset += 4
        else:
            break
    
    return result

def decode_hex(H):
    R = hex(H)
    F = str(R)[2:]
    if len(F) == 1:
        F = "0" + F
    return F

def fix_packet(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {}
        field_data['wire_type'] = result.wire_type
        if result.wire_type == "varint":
            field_data['data'] = result.data
        if result.wire_type == "string":
            field_data['data'] = result.data
        if result.wire_type == "bytes":
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = fix_packet(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

def decode_packet(input_text):
    try:
        parsed_results = Parser().parse(input_text)
        parsed_results_objects = parsed_results
        parsed_results_dict = fix_packet(parsed_results_objects)
        json_data = json.dumps(parsed_results_dict)
        return json_data
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[PACKET DECODE ERROR] {e}")
        return None

def create_packet(Pk, N, K, V):
    PkEnc = AES.new(K , AES.MODE_CBC , V).encrypt(pad(bytes.fromhex(Pk) ,16)).hex()
    _ = decode_hex(int(len(PkEnc) // 2))
    if len(_) == 2: HeadEr = N + "000000"
    elif len(_) == 3: HeadEr = N + "00000"
    elif len(_) == 4: HeadEr = N + "0000"
    elif len(_) == 5: HeadEr = N + "000"
    else: print('ErroR => GeneRatinG ThE PacKeT !! ')
    return bytes.fromhex(HeadEr + _ + PkEnc)

def create_auth_token_online(account_id, jwt_token, timestamp, key, iv):
    try:
        # Key / IV may come as hex string OR bytes
        if isinstance(key, str):
            K = bytes.fromhex(key)
        else:
            K = key
        if isinstance(iv, str):
            V = bytes.fromhex(iv)
        else:
            V = iv

        # AES-CBC encrypt JWT with PKCS7 padding
        jwt_bytes = jwt_token.encode('utf-8')
        encrypted_packet = AES.new(K, AES.MODE_CBC, V).encrypt(
            pad(jwt_bytes, AES.block_size)
        )

        # Build 22-byte header
        header = (
            bytes.fromhex('7319') +                          # packet type
            int(account_id).to_bytes(8, 'big') +             # 8-byte account_id
            int(timestamp).to_bytes(4, 'big') +              # 4-byte timestamp
            b'\x00\x00\x00\x00' +                            # 4-byte zeros
            len(encrypted_packet).to_bytes(4, 'big')         # 4-byte length
        )

        return (header + encrypted_packet).hex()

    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[AUTH TOKEN ERROR] {e}")
        return None

def create_auth_token_chat(account_id, jwt_token, timestamp, key, iv):
    try:
        K = bytes.fromhex(key) if isinstance(key, str) else key
        V = bytes.fromhex(iv)  if isinstance(iv,  str) else iv

        jwt_bytes = jwt_token.encode('utf-8')
        ct = AES.new(K, AES.MODE_CBC, V).encrypt(
            pad(jwt_bytes, AES.block_size)
        )

        uid_b = int(account_id).to_bytes(8, 'big')
        ts_b  = int(timestamp).to_bytes(4, 'big')
        len_b = len(ct).to_bytes(4, 'big')

        header = bytes.fromhex('6d19') + uid_b + ts_b + len_b
        
        return (header + ct).hex()

    except Exception as e:
        print(f"[AUTH TOKEN ERROR] {e}")
        return None

async def equip_default_emote():
    try:
        url = f"{server_url}/ChooseEmote"
        fields = {
          "6": {
              "1": 1,
              "2": 909000001
          }
        }

        proto_bytes = create_proto(fields).hex()
        payload = bytes.fromhex(encrypt_aes(proto_bytes))
        headers = {
            "authorization": f"Bearer {jwt_token}",
            "host": server_url.replace("https://", "").replace("http://", "").split("/")[0],
            "x-ga": "v1 1",
            "content-type": "application/x-www-form-urlencoded",
            "accept-encoding": "deflate, gzip",
            "releaseversion": f"{release_version}",
            "user-agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "accept": "*/*",
            "x-unity-version": "2022.3.47f1"
        }
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, data=payload) as response:
                response_content = await response.read()
                if response.status == 200:
                    return True 
                else:
                    print(f"{Style.BRIGHT}{Fore.RED}[ACCEPT REQUEST ERROR] Status Code: {response.status}")
                    print(f"{Style.BRIGHT}{Fore.RED}[ACCEPT REQUEST ERROR] {response_content}")
                    return None
    except asyncio.TimeoutError:
        print(f"{Style.BRIGHT}{Fore.RED}[ACCEPT REQUEST ERROR] TIMEOUT! Request took longer than 5 seconds!")
        return None
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[ACCEPT REQUEST ERROR] {e}")
        return None

async def accept_friend_request(uid):
    try:
        url = f"{server_url}/ConfirmFriendRequest"
        fields = {
            "1": int(uid),
            "2": int(account_id)
        }
        proto_bytes = create_proto(fields).hex()
        payload = bytes.fromhex(encrypt_aes(proto_bytes))
        headers = {
            "authorization": f"Bearer {jwt_token}",
            "host": server_url.replace("https://", "").replace("http://", "").split("/")[0],
            "x-ga": "v1 1",
            "content-type": "application/x-www-form-urlencoded",
            "accept-encoding": "deflate, gzip",
            "releaseversion": f"{release_version}",
            "user-agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "accept": "*/*",
            "x-unity-version": "2022.3.47f1"
        }
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, data=payload) as response:
                response_content = await response.read()
                if response.status == 200:
                    decoded_json = decode_protobuf(response_content)
                    #print(decoded_json)
                    return decoded_json
                else:
                    print(f"{Style.BRIGHT}{Fore.RED}[ACCEPT REQUEST ERROR] Status Code: {response.status}")
                    print(f"{Style.BRIGHT}{Fore.RED}[ACCEPT REQUEST ERROR] {response_content}")
                    return None
    except asyncio.TimeoutError:
        print(f"{Style.BRIGHT}{Fore.RED}[ACCEPT REQUEST ERROR] TIMEOUT! Request took longer than 5 seconds!")
        return None
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[ACCEPT REQUEST ERROR] {e}")
        return None

async def accept_clan_request(owner_uid, clan_id):
    try:
        url = f"{server_url}/ApproveJoinClanInvitation"
        fields = {
            "1": int(owner_uid),
            "2": int(clan_id)
        }
        proto_bytes = create_proto(fields).hex()
        payload = bytes.fromhex(encrypt_aes(proto_bytes))
        headers = {
            "authorization": f"Bearer {jwt_token}",
            "host": server_url.replace("https://", "").replace("http://", "").split("/")[0],
            "x-ga": "v1 1",
            "content-type": "application/x-www-form-urlencoded",
            "accept-encoding": "deflate, gzip",
            "releaseversion": f"{release_version}",
            "user-agent": "UnityPlayer/2022.3.47f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "accept": "*/*",
            "x-unity-version": "2022.3.47f1"
        }
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, data=payload) as response:
                response_content = await response.read()
                if response.status == 200:
                    decoded_json = decode_protobuf(response_content)
                    print(decoded_json)
                    return decoded_json
                else:
                    print(f"{Style.BRIGHT}{Fore.RED}[ACCEPT REQUEST ERROR] Status Code: {response.status}")
                    print(f"{Style.BRIGHT}{Fore.RED}[ACCEPT REQUEST ERROR] {response_content}")
                    return None
    except asyncio.TimeoutError:
        print(f"{Style.BRIGHT}{Fore.RED}[ACCEPT REQUEST ERROR] TIMEOUT! Request took longer than 5 seconds!")
        return None
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[ACCEPT REQUEST ERROR] {e}")
        return None

async def update():
    try:
        game_version = "1.132.1" #play_scraper("com.dts.freefireth").get('version', None)
        print(f"{Style.BRIGHT}{Fore.CYAN}[UPDATE] {Fore.MAGENTA}Game Version: {game_version}")
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(f'https://version.ggwhitehawk.com/live/ver.php?version={game_version}&lang=en&device=android&channel=android&appsttore=googleplay&region=ME&whitelist_version=1.3.0&whitelist_sp_version=1.0.0&device_name=google%20G011A&device_CPU=ARMv7%20VFPv3%20NEON%20VMH&device_GPU=Adreno%20(TM)%20640&device_mem=1993') as response:
                text_data = await response.text()
                json_data = json.loads(text_data)
                release_version = json_data.get('latest_release_version', None)
                print(f"{Style.BRIGHT}{Fore.CYAN}[UPDATE] {Fore.MAGENTA}Release Version: {release_version}")
                login_url = json_data.get('server_url', None)
                print(f"{Style.BRIGHT}{Fore.CYAN}[UPDATE] {Fore.MAGENTA}Login Url: {login_url}")
                game_version = json_data.get('remote_version', None) if 'remote_version' in json_data else game_version
                print(f"{Style.BRIGHT}{Fore.CYAN}[UPDATE] {Fore.MAGENTA}Remote Version: {game_version}")
                return game_version, release_version, login_url 
    except asyncio.TimeoutError:
        print(f"{Style.BRIGHT}{Fore.RED}[UPDATE ERROR] TIMEOUT! Request took longer than 5 seconds!")
        return None, None, None 
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[UPDATE ERROR] {e}")
        return None, None, None 

async def get_access_token_v2(uid, password):
    try:
        url = "https://ffmconnect.ppmainecoonghj.com/api/v2/oauth/guest/token:grant"
        
        data = {
            "uid": uid,
            "password": password,
            "client_id": 100067,
            "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            "client_type": 2,
            "response_type": "token"
        }
        
        headers = {
            "Host": "ffmconnect.ppmainecoonghj.com",
            "User-Agent": "GarenaMSDK/4.0.42(SM-E135F ;Android 14;en;GB;app 2.130.1 2019118332;)",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Cookie": "datadome=EOwGRujHHVmJVPaGZLYGhV8QFGW2a~4NrrAcRYxKrt~MdvZfwj8_BSzLdf3ua1JZHtyf~lxEN~ZcSCB0jGvCU_7L7z05sWA5F~XoVD1Ne0SIwO4Piuf7lzTmJp7k0Uc9"
        }
        
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        json_data = json.loads(response_text)
                        if json_data.get('code') == 0:
                            token_data = json_data.get('data', {})
                            access_token = token_data.get('access_token', None)
                            open_id = token_data.get('open_id', None)
                            platform = token_data.get('platform', None)
                            refresh_token = token_data.get('refresh_token', None)
                            uid_returned = token_data.get('uid', None)
                            expires_in = token_data.get('expires_in', None)
                            
                            print(f"{Style.BRIGHT}{Fore.CYAN}[ACCESS TOKEN V2] {Fore.GREEN}Access Token: {access_token}")
                            print(f"{Style.BRIGHT}{Fore.CYAN}[ACCESS TOKEN V2] {Fore.GREEN}Open ID: {open_id}")
                            print(f"{Style.BRIGHT}{Fore.CYAN}[ACCESS TOKEN V2] {Fore.GREEN}Platform: {platform}")
                            print(f"{Style.BRIGHT}{Fore.CYAN}[ACCESS TOKEN V2] {Fore.GREEN}Refresh Token: {refresh_token[:30]}...")
                            print(f"{Style.BRIGHT}{Fore.CYAN}[ACCESS TOKEN V2] {Fore.GREEN}UID: {uid_returned}")
                            print(f"{Style.BRIGHT}{Fore.CYAN}[ACCESS TOKEN V2] {Fore.GREEN}Expires In: {expires_in} seconds")
                            
                            return access_token, open_id, platform
                        else:
                            error_msg = json_data.get('error', 'Unknown error')
                            print(f"{Style.BRIGHT}{Fore.RED}[ACCESS TOKEN V2 ERROR] API Error: {error_msg}")
                            print(f"{Style.BRIGHT}{Fore.RED}[ACCESS TOKEN V2 ERROR] Response: {response_text}")
                            return None, None, None
                    except json.JSONDecodeError:
                        print(f"{Style.BRIGHT}{Fore.RED}[ACCESS TOKEN V2 ERROR] Invalid JSON response")
                        print(f"{Style.BRIGHT}{Fore.RED}[ACCESS TOKEN V2 ERROR] Response: {response_text[:200]}")
                        return None, None, None
                else:
                    print(f"{Style.BRIGHT}{Fore.RED}[ACCESS TOKEN V2 ERROR] Status Code: {response.status}")
                    print(f"{Style.BRIGHT}{Fore.RED}[ACCESS TOKEN V2 ERROR] Response: {response_text}")
                    return None, None, None
                
    except asyncio.TimeoutError:
        print(f"{Style.BRIGHT}{Fore.RED}[ACCESS TOKEN V2 ERROR] TIMEOUT! Request took longer than 10 seconds!")
        return None, None, None
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[ACCESS TOKEN V2 ERROR] {e}")
        import traceback
        traceback.print_exc()
        return None, None, None 

async def get_payload(access_token, open_id, platform, version):
    # ---------- MajorLogin ----------
    major_login = {
        "3": str(datetime.now())[:-7],
        "4": "free fire",
        "5": 1,
        "7": f"{version}",
        "8": "Android OS 14 / API-34 (UP1A.231005.007/E135FXXSEEZE2)",
        "9": "Handheld",
        "11": "CarrierDataNetwork",
        "12": 1672,
        "13": 750,
        "14": "338",
        "15": "ARMv7 VFPv3 NEON | 2002 | 8",
        "16": 3702,
        "17": "Mali-G52",
        "18": "OpenGL ES 3.2 v1.r38p1-01bet0-mbs2v41_0.6d20ec041e51b2f2d25dfc265586ebe8",
        "19": f"Google|{uuid.uuid4()}",
        "21": "en",
        "22": f"{open_id}",
        "23": f"{platform}",
        "24": "Handheld",
        "25": "samsung SM-E135F",
        "26": "BD",
        "29": f"{access_token}",
        "30": 1,
        "42": "Cellular",
        "57": "7428b253defc164018c604a1ebbfebdf",
        "60": 52037,
        "61": 5355,
        "62": 3723,
        "63": 3,
        "64": 5483,
        "65": 52037,
        "66": 5483,
        "67": 52037,
        "73": 2,
        "74": "/data/app/~~yACsV8QOk9OexgajWQP30A==/com.dts.freefireth-Bi_wPVrrhYM2nYncc29q7Q==/lib/arm",
        "76": 1,
        "77": "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~yACsV8QOk9OexgajWQP30A==/com.dts.freefireth-Bi_wPVrrhYM2nYncc29q7Q==/base.apk",
        "78": 3,
        "79": 1,
        "81": "32",
        "83": "2019121229",
        "86": "OpenGLES2",
        "87": 8191,
        "88": int(platform),
        "92": 16091,
        "93": "android",
        "94": "KqsHT3Yeqo3RLRl8efNiL3aL/1SHwlSrtK0DwNAqdkNBQz70TeVy+icaIwuR3UK4b65Uf3IG5xBFEv0uu+jQZI+rOYCmNCsXjJT4QcZaYgoaaUGG",
        "95": 111107,
        "96": "{\"cur_rate\":null,\"support_etc2\":false}",
        "97": 1,
        "98": 1,
        "99": f"{platform}",
        "100": f"{platform}",
        "102": "4503454457550c0766",
        "104": 53792,
        "105": 1,
        "106": "https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|6b2078db9d22dd98f8e9386a39af8462",
        "107": "c8e41b7a93f02d56e1a94c7b8203f5d1"
    }

    # ---------- GetLoginData ----------
    get_login_data = {
        "3": str(datetime.now())[:-7],
        "4": "free fire",
        "5": 1,
        "7": f"{version}",
        "8": "Android OS 14 / API-34 (UP1A.231005.007/E135FXXSEEZE2)",
        "9": "Handheld",
        "11": "CarrierDataNetwork",
        "12": 1672,
        "13": 750,
        "14": "338",
        "15": "ARMv7 VFPv3 NEON | 2002 | 8",
        "16": 3702,
        "17": "Mali-G52",
        "18": "OpenGL ES 3.2 v1.r38p1-01bet0-mbs2v41_0.6d20ec041e51b2f2d25dfc265586ebe8",
        "19": f"Google|{uuid.uuid4()}",
        "20": "104.28.197.151",
        "21": "en",
        "22": f"{open_id}",
        "23": f"{platform}",
        "24": "Handheld",
        "25": "samsung SM-E135F",
        "26": "BD",
        "29": f"{access_token}",
        "30": 1,
        "42": "Cellular",
        "57": "7428b253defc164018c604a1ebbfebdf",
        "60": 52037,
        "61": 5355,
        "62": 3723,
        "63": 3,
        "64": 5483,
        "65": 52037,
        "66": 5483,
        "67": 52037,
        "73": 2,
        "74": "/data/app/~~yACsV8QOk9OexgajWQP30A==/com.dts.freefireth-Bi_wPVrrhYM2nYncc29q7Q==/lib/arm",
        "76": 1,
        "77": "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~yACsV8QOk9OexgajWQP30A==/com.dts.freefireth-Bi_wPVrrhYM2nYncc29q7Q==/base.apk",
        "78": 3,
        "79": 1,
        "81": "32",
        "83": "2019121229",
        "86": "OpenGLES2",
        "87": 8191,
        "88": int(platform),
        "90": "Khulna",
        "91": "D",
        "92": 16091,
        "93": "android",
        "94": "KqsHT3Yeqo3RLRl8efNiL3aL/1SHwlSrtK0DwNAqdkNBQz70TeVy+icaIwuR3UK4b65Uf3IG5xBFEv0uu+jQZI+rOYCmNCsXjJT4QcZaYgoaaUGG",
        "95": 111107,
        "96": "{\"cur_rate\":null,\"support_etc2\":false}",
        "97": 1,
        "98": 1,
        "99": "0",
        "100": f"{platform}",
        "102": "4503454457550c0766",
        "103": 1,
        "104": 53792,
        "105": 1,
        "106": "https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|6b2078db9d22dd98f8e9386a39af8462",
        "107": "c8e41b7a93f02d56e1a94c7b8203f5d1"
    }

    proto_bytes1 = create_proto(major_login).hex()
    proto_bytes2 = create_proto(get_login_data).hex()
    encrypted1 = bytes.fromhex(encrypt_aes(proto_bytes1))
    encrypted2 = bytes.fromhex(encrypt_aes(proto_bytes2))
    return encrypted1, encrypted2

async def major_login(payload, login_url, release_version):
    try:
        url = f"{login_url}MajorLogin"
        headers = {
            "Accept": "*/*",
            "Authorization": "Bearer ",
            "Content-Type": "application/x-www-form-urlencoded",
            "ReleaseVersion": f"{release_version}",
            "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "X-GA": "v1 1",
            "X-GA-SV": str(int(time.time())),
            "X-Unity-Version": "2018.4.12f1"
        }
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, data=payload) as response:
                response_content = await response.read()
                if response.status == 200:
                    print(f"{Style.BRIGHT}{Fore.CYAN}[MAJOR LOGIN] {Fore.MAGENTA}Status Code: {response.status}")
                    print(f"{Style.BRIGHT}{Fore.CYAN}[MAJOR LOGIN] {Fore.MAGENTA}Response Length: {len(response_content)} bytes")
                    print(f"{Style.BRIGHT}{Fore.CYAN}[MAJOR LOGIN] {Fore.MAGENTA}First 80 bytes: {response_content[:80].hex()}")
                    
                    # NEW: Skip 64-byte wrapper header
                    PROTO_HEADER_SIZE = 64
                    
                    if len(response_content) > PROTO_HEADER_SIZE:
                        decoded_json = decode_protobuf(response_content[PROTO_HEADER_SIZE:])
                        print(decoded_json)
                    else:
                        decoded_json = decode_protobuf(response_content)
                    
                    print(f"{Style.BRIGHT}{Fore.CYAN}[MAJOR LOGIN] {Fore.GREEN}Decoded Fields: {list(decoded_json.keys()) if decoded_json else 'None'}")
                    return decoded_json
                else:
                    print(f"{Style.BRIGHT}{Fore.RED}[MAJOR LOGIN ERROR] Status Code: {response.status}")
                    print(f"{Style.BRIGHT}{Fore.RED}[MAJOR LOGIN ERROR] {response_content}")
                    return None
    except asyncio.TimeoutError:
        print(f"{Style.BRIGHT}{Fore.RED}[MAJOR LOGIN ERROR] TIMEOUT! Request took longer than 5 seconds!")
        return None
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[MAJOR LOGIN ERROR] {e}")
        return None

async def get_login_data(payload, jwt_token, server_url, release_version):
    try:
        url = f"{server_url}/GetLoginData"
        headers = {
            "Accept": "*/*",
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "ReleaseVersion": f"{release_version}",
            "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "X-GA": "v1 1",
            "X-GA-SV": str(int(time.time())),  # Live timestamp
            "X-Unity-Version": "2018.4.12f1"
        }
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, data=payload) as response:
                response_content = await response.read()
                if response.status == 200:
                    print(f"{Style.BRIGHT}{Fore.CYAN}[LOGIN DATA] {Fore.MAGENTA}Status Code: {response.status}")
                    decoded_json = decode_protobuf(response_content)
                    print(decoded_json)
                    return decoded_json
                else:
                    print(f"{Style.BRIGHT}{Fore.RED}[LOGIN DATA ERROR] Status Code: {response.status}")
                    print(f"{Style.BRIGHT}{Fore.RED}[LOGIN DATA ERROR] {response_content}")
                    return None
    except asyncio.TimeoutError:
        print(f"{Style.BRIGHT}{Fore.RED}[LOGIN DATA ERROR] TIMEOUT! Request took longer than 5 seconds!")
        return None 
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[LOGIN DATA ERROR] {e}")
        return None 

async def send_packet(packet, packet_type):
    try:
        if packet_type == 'chat':
            if chat_writer:
                chat_writer.write(packet)
                await chat_writer.drain()
                print(f"{Style.BRIGHT}{Fore.CYAN}[PACKET SEND] {Fore.GREEN}Packet Sent On Server: {packet_type}")
            else:
                print(f"{Style.BRIGHT}{Fore.RED}[PACKET SEND ERROR] chat_writer Not Ready!")
        elif packet_type == 'online':
            if online_writer:
                online_writer.write(packet)
                await online_writer.drain()
                print(f"{Style.BRIGHT}{Fore.CYAN}[PACKET SEND] {Fore.GREEN}Packet Sent On Server: {packet_type}")
            else:
                print(f"{Style.BRIGHT}{Fore.RED}[PACKET SEND ERROR] online_writer Not Ready!")
        else:
            print(f"{Style.BRIGHT}{Fore.RED}[PACKET SEND ERROR] Unsupported Packed Server")
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[PACKET SEND ERROR] {e}")

async def udp_task(json_data, key, iv, region):
    """
    UDP flow (robust, real-client compatible):
        HELLO → server ACK → server HELLO echo
              → client ACK mirror → client PING1 → server PING1 reply
              → client PING2 → server PING2 reply
              → PREPARE + POST → wait JOIN_MATCH
              → JOIN ACK + start all background tasks
              → monitoring → BYEBYE → stop all → exit
    """
    print(f"{Style.BRIGHT}{Fore.GREEN}★ MATCH SERVER DETECTED — HELLO + ACK + PING + PREPARE + POST{Style.RESET_ALL}")

    ping_stop  = None; ping_task  = None
    sync_stop  = None; sync_task  = None
    ack_stop   = None; ack_task   = None
    state_stop = None; state_task = None
    emote_stop = None; emote_task = None
    sock = None

    ack_counter_holder = [_ACK_COUNTER_BASE]

    try:
        field5 = json_data.get("5", {}).get("data", {})
        if not isinstance(field5, dict):
            print(f"{Style.BRIGHT}{Fore.RED}[MATCH] field 5 not dict!{Style.RESET_ALL}")
            return

        server_addr = field5.get("2", {}).get("data")
        udp_key_hex = field5.get("3", {}).get("data")
        jwt_token   = field5.get("4", {}).get("data")
        match_code  = field5.get("42", {}).get("data")
        block_val   = field5.get("1", {}).get("data")

        print(f"{Style.BRIGHT}{Fore.GREEN}[MATCH] Server    : {server_addr}{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}{Fore.GREEN}[MATCH] UDP Key   : {udp_key_hex}{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}{Fore.GREEN}[MATCH] Match Code: {match_code}{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}{Fore.GREEN}[MATCH] Block Val : {block_val}{Style.RESET_ALL}")
        print(f"{Style.BRIGHT}{Fore.GREEN}[MATCH] JWT len   : {len(jwt_token) if jwt_token else 0}{Style.RESET_ALL}")

        if not server_addr or ":" not in str(server_addr):
            print(f"{Style.BRIGHT}{Fore.RED}[MATCH] Invalid server address!{Style.RESET_ALL}")
            return

        ip, port = str(server_addr).split(":")
        port = int(port)
        print(f"{Style.BRIGHT}{Fore.CYAN}[MATCH] {region.upper()} UDP → {ip}:{port}{Style.RESET_ALL}")

        loop = asyncio.get_event_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.connect((ip, port))
        except Exception as e:
            print(f"{Style.BRIGHT}{Fore.RED}[MATCH] UDP connect error: {e}{Style.RESET_ALL}")
            sock.close()
            return

        udp_key_b = bytes.fromhex(udp_key_hex)
        k = udp_key_b[0]
        v80 = ((k << 8) | k) & 0xFFFF
        print(f"{Style.BRIGHT}{Fore.CYAN}[MATCH] k=0x{k:02X}  v80=0x{v80:04X}{Style.RESET_ALL}")

        # ── layout: remove code 2 for ACK, keep full for HELLO/PREPARE/POST ──
        try:
            layout_full = [int(c) for c in str(match_code).strip()]
            layout_nr   = [c for c in layout_full if c != 2]
        except Exception:
            layout_full = [0, 4, 1, 3, 2]
            layout_nr   = [0, 4, 1, 3]
        print(f"{Style.BRIGHT}{Fore.CYAN}[MATCH] layout_full={layout_full}  layout_nr={layout_nr}{Style.RESET_ALL}")

        response_layouts = [
            layout_nr, layout_full,
            [0, 4, 1, 3, 2], [0, 4, 1, 2, 3],
            [0, 4, 1, 3], [0, 3, 1, 2, 4],
            [0, 3, 4, 1], [0, 1, 4, 3], [3, 1, 4, 0], [0, 1, 4, 3, 2],
        ]

        def _log(cmd, msg):
            if cmd not in SKIP_UDP_LOG:
                print(msg)

        # ═══════════════════════════════════════════════════════
        #  ★ FIX 1: PING builder — 4-byte counter + 3 zeros = 7 bytes
        # ═══════════════════════════════════════════════════════
        async def build_ping(counter4: bytes, msg_key: int):
            k_ = udp_key_b[0]; v80_ = ((k_ << 8) | k_) & 0xFFFF
            content = counter4[:4] + b"\x00\x00\x00"   # ★ 7 bytes
            hdr = await encode_header(layout_nr, 0, 3, 0, 0, len(content), k_, v80_)
            pkt = bytearray([msg_key, 0x00]) + hdr + content
            pkt[1] = await crc7_buff(0, bytes(pkt[2:])) & 0x7F
            return bytes(pkt)

        # ── PREPARE ──
        async def build_prepare(account_id, block_val, udp_key, layout, jwt_token, jwt_len=660):
            jwt_part = jwt_token[:jwt_len].encode() if jwt_token else b""
            content = (await has_ssan_zig(len(jwt_part))) + jwt_part
            return await build_packet(0x63, layout, 2, 447, 0, 1, content, udp_key)

        # ── POST ──
        async def build_post(account_id, block_val, host, jwt_token, udp_key, layout,
                             name=b"", mid=None, hex_part=None, msg_key=0x5A):
            if mid is None:      mid = DEFAULT_MID
            if hex_part is None: hex_part = DEFAULT_HEX_PART

            c = bytearray()
            c += await uleb_encode(account_id)
            c += await uleb_encode(block_val)
            c += await uleb_encode(1)
            c += await uleb_encode(15)
            c += await uleb_encode(block_val)
            c += await uleb_encode(1)
            c += b"\x00" * 6
            c += FIXED_MIDDLE
            c += b"\x00\x00\x00"
            c += b"\x00\x00\x01\x00\x00"
            c += bytes([len(name) * 2])
            c += name
            c += mid
            host_b = host.encode()
            c += bytes([len(host_b) * 2])
            c += host_b
            c += b"\x80\x01"
            c += hex_part

            jwt_parts = jwt_token.split(".")
            if len(jwt_parts) >= 3:
                payload_b64 = jwt_parts[1]
                sig         = jwt_parts[2]
                K = len(payload_b64) - 623
                if K <= 0 or K > len(payload_b64):
                    K = 204
                jwt_sig = (payload_b64[-K:] + "." + sig).encode()
                c += await uleb_encode(len(jwt_sig) * 2)
                c += jwt_sig

            content = bytes(c)
            pkt = await build_packet(msg_key, layout, 2, 448, 1, 1, content, udp_key)
            return pkt, content

        def _print_decoded(tag, decoded, direction):
            cmd = decoded["cmd"]
            if cmd in SKIP_UDP_LOG:
                return
            cmd_name = MESSAGE_ID_TO_NAME.get(cmd, f"UNKNOWN_{cmd}")
            print(f"{Style.BRIGHT}{Fore.GREEN}  [{tag}][{direction}] k=0x{decoded['k']:02X}  "
                  f"layout={decoded['layout']}  sendOpt={decoded['sendOption']}  "
                  f"cmd={cmd} ({cmd_name})  flags={decoded['flags']}  len={decoded['length']}{Style.RESET_ALL}")

        # ═══ SEND HELLO ═══
        try:
            hello_hex = await build_hello_packet(account_id, udp_key_b, match_code)
            hello_bytes = bytes.fromhex(hello_hex)
            await loop.sock_sendto(sock, hello_bytes, (ip, port))
            print(f"{Style.BRIGHT}{Fore.CYAN}[HELLO] sent {len(hello_bytes)}B{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Style.BRIGHT}{Fore.RED}[HELLO ERROR] {e}{Style.RESET_ALL}")
            sock.close()
            return

        # ═══════════════════════════════════════════════════════
        #  STATE MACHINE
        # ═══════════════════════════════════════════════════════
        saved_ack       = None
        ping1_counter   = None
        ping2_counter   = None
        state           = "waiting_for_ack"
        join_match_received = False
        hello_retransmit    = 0
        last_hello_time     = time.time()
        ping_retry_count    = 0
        MAX_PING_RETRIES    = 5

        while True:
            try:
                # Retransmit HELLO every 2s while waiting for ACK
                if state == "waiting_for_ack" and (time.time() - last_hello_time) > 2.0:
                    hello_retransmit += 1
                    try:
                        await loop.sock_sendto(sock, hello_bytes, (ip, port))
                        print(f"{Style.BRIGHT}{Fore.YELLOW}[HELLO] retransmit #{hello_retransmit}{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Style.BRIGHT}{Fore.RED}[HELLO RETX] {e}{Style.RESET_ALL}")
                    last_hello_time = time.time()

                data = await asyncio.wait_for(loop.sock_recv(sock, 65535), timeout=30.0)
                if not data:
                    continue

                decoded = _decode_response(data, preferred_layouts=response_layouts)
                if decoded is None:
                    continue

                cmd = decoded["cmd"]

                if cmd not in SKIP_UDP_LOG:
                    print(f"{Style.BRIGHT}{Fore.CYAN}[RECV] {len(data)}B: {data.hex()[:60]}...{Style.RESET_ALL}")
                    _print_decoded("RECV", decoded, "S→C")

                # ★ BYEBYE
                if cmd == 4:
                    _log(cmd, f"{Style.BRIGHT}{Fore.YELLOW}[BYEBYE] Match ended — stopping all tasks{Style.RESET_ALL}")
                    for ev in (ping_stop, sync_stop, ack_stop, state_stop, emote_stop):
                        if ev is not None: ev.set()
                    for t in (ping_task, sync_task, ack_task, state_task, emote_task):
                        if t is not None:
                            t.cancel()
                            try: await t
                            except (asyncio.CancelledError, Exception): pass
                    try: sock.close()
                    except: pass
                    _log(cmd, f"{Style.BRIGHT}{Fore.GREEN}[MATCH ENDED]{Style.RESET_ALL}")
                    return

                # ═══════════════════════════════════════════════
                #  STATE 1: wait for server ACK
                # ═══════════════════════════════════════════════
                if state == "waiting_for_ack":
                    if cmd == 2:
                        saved_ack = data
                        state = "waiting_for_hello"
                        _log(cmd, f"{Style.BRIGHT}{Fore.GREEN}[STATE 1] ACK received ({len(data)}B) → waiting_for_hello{Style.RESET_ALL}")
                    else:
                        print(f"{Style.BRIGHT}{Fore.YELLOW}[STATE 1] got cmd={cmd}, expected 2{Style.RESET_ALL}")

                # ═══════════════════════════════════════════════
                #  STATE 2: wait for server HELLO echo
                # ═══════════════════════════════════════════════
                elif state == "waiting_for_hello":
                    if cmd == 1:
                        # ★ FIX 2: send ACK mirror with msg_key 0x6A
                        ack_mirror = bytearray(saved_ack)
                        ack_mirror[0] = 0x6A                          # ★ real client uses 0x6A
                        await loop.sock_sendto(sock, bytes(ack_mirror), (ip, port))
                        _log(cmd, f"{Style.BRIGHT}{Fore.CYAN}[STATE 2] ACK mirror sent (0x6A){Style.RESET_ALL}")

                        # ★ FIX 3: small delay before PING
                        await asyncio.sleep(0.15)

                        # ★ FIX 4: PING counter = random 4 bytes
                        ping1_counter = os.urandom(4)
                        ping1_pkt = await build_ping(ping1_counter, msg_key=0x68)
                        await loop.sock_sendto(sock, ping1_pkt, (ip, port))
                        _log(cmd, f"{Style.BRIGHT}{Fore.CYAN}[STATE 2] PING1 sent counter={ping1_counter.hex()} (7B body){Style.RESET_ALL}")

                        state = "waiting_for_ping1_reply"
                        ping_retry_count = 0
                    else:
                        print(f"{Style.BRIGHT}{Fore.YELLOW}[STATE 2] got cmd={cmd}, expected 1{Style.RESET_ALL}")

                # ═══════════════════════════════════════════════
                #  STATE 3: wait for PING1 reply
                # ═══════════════════════════════════════════════
                elif state == "waiting_for_ping1_reply":
                    if cmd == 3:
                        _log(cmd, f"{Style.BRIGHT}{Fore.GREEN}[STATE 3] PING1 reply ✓{Style.RESET_ALL}")
                        await asyncio.sleep(0.15)
                        ping2_counter = os.urandom(4)
                        ping2_pkt = await build_ping(ping2_counter, msg_key=0x6D)
                        await loop.sock_sendto(sock, ping2_pkt, (ip, port))
                        _log(cmd, f"{Style.BRIGHT}{Fore.CYAN}[STATE 3] PING2 sent counter={ping2_counter.hex()}{Style.RESET_ALL}")
                        state = "waiting_for_ping2_reply"

                    # ★ FIX 5: server re-sent HELLO → re-ACK + re-PING
                    elif cmd == 1:
                        ping_retry_count += 1
                        if ping_retry_count > MAX_PING_RETRIES:
                            print(f"{Style.BRIGHT}{Fore.RED}[STATE 3] MAX retries exceeded — giving up{Style.RESET_ALL}")
                            break
                        print(f"{Style.BRIGHT}{Fore.YELLOW}[STATE 3] HELLO re-received — retry ACK + PING1 (#{ping_retry_count}){Style.RESET_ALL}")

                        ack_mirror = bytearray(saved_ack)
                        ack_mirror[0] = 0x6A
                        await loop.sock_sendto(sock, bytes(ack_mirror), (ip, port))
                        await asyncio.sleep(0.15)

                        ping1_counter = os.urandom(4)
                        ping1_pkt = await build_ping(ping1_counter, msg_key=0x68)
                        await loop.sock_sendto(sock, ping1_pkt, (ip, port))
                        print(f"{Style.BRIGHT}{Fore.CYAN}[STATE 3] PING1 re-sent counter={ping1_counter.hex()}{Style.RESET_ALL}")

                    else:
                        print(f"{Style.BRIGHT}{Fore.YELLOW}[STATE 3] got cmd={cmd}, expected 3{Style.RESET_ALL}")

                # ═══════════════════════════════════════════════
                #  STATE 4: wait for PING2 reply → PREPARE + POST
                # ═══════════════════════════════════════════════
                elif state == "waiting_for_ping2_reply":
                    if cmd == 3:
                        _log(cmd, f"{Style.BRIGHT}{Fore.GREEN}[STATE 4] PING2 reply ✓ → PREPARE + POST{Style.RESET_ALL}")

                        # PREPARE
                        try:
                            prepare_pkt = await build_prepare(
                                account_id=account_id, block_val=block_val,
                                udp_key=udp_key_b, layout=layout_full,
                                jwt_token=jwt_token, jwt_len=660,
                            )
                            await loop.sock_sendto(sock, prepare_pkt, (ip, port))
                            _log(cmd, f"{Style.BRIGHT}{Fore.GREEN}[PREPARE] sent ({len(prepare_pkt)}B){Style.RESET_ALL}")
                        except Exception as e:
                            print(f"{Style.BRIGHT}{Fore.RED}[PREPARE ERROR] {e}{Style.RESET_ALL}")
                            traceback.print_exc()

                        await asyncio.sleep(0.15)

                        # POST
                        try:
                            post_pkt, post_content = await build_post(
                                account_id=account_id, block_val=block_val,
                                host=str(server_addr), jwt_token=jwt_token,
                                udp_key=udp_key_b, layout=layout_full,
                                name=b"", mid=DEFAULT_MID, hex_part=DEFAULT_HEX_PART,
                                msg_key=0x5A,
                            )
                            await loop.sock_sendto(sock, post_pkt, (ip, port))
                            _log(cmd, f"{Style.BRIGHT}{Fore.GREEN}[POST] sent ({len(post_pkt)}B)  host={server_addr}{Style.RESET_ALL}")
                        except Exception as e:
                            print(f"{Style.BRIGHT}{Fore.RED}[POST ERROR] {e}{Style.RESET_ALL}")
                            traceback.print_exc()

                        state = "monitoring"
                        _log(cmd, f"{Style.BRIGHT}{Fore.YELLOW}[STATE] → monitoring (waiting for JOIN_MATCH){Style.RESET_ALL}")

                        # Keepalive PING (starts immediately)
                        ping_stop = asyncio.Event()
                        ping_task = asyncio.create_task(
                            _keepalive_ping(sock, ip, port, udp_key_b, layout_nr, ping_stop)
                        )
                        _log(cmd, f"{Style.BRIGHT}{Fore.CYAN}[KEEPALIVE] started (1s){Style.RESET_ALL}")

                    elif cmd == 1:
                        # Re-received HELLO in state 4 → redo state 3
                        print(f"{Style.BRIGHT}{Fore.YELLOW}[STATE 4] HELLO re-received — back to PING{Style.RESET_ALL}")
                        ack_mirror = bytearray(saved_ack); ack_mirror[0] = 0x6A
                        await loop.sock_sendto(sock, bytes(ack_mirror), (ip, port))
                        await asyncio.sleep(0.15)
                        ping1_counter = os.urandom(4)
                        ping1_pkt = await build_ping(ping1_counter, msg_key=0x68)
                        await loop.sock_sendto(sock, ping1_pkt, (ip, port))
                        state = "waiting_for_ping1_reply"

                # ═══════════════════════════════════════════════
                #  MONITORING
                # ═══════════════════════════════════════════════
                else:
                    if cmd == 100 and not join_match_received:
                        _log(cmd, f"{Style.BRIGHT}{Fore.YELLOW}★ JOIN_MATCH → ACK + start all tasks{Style.RESET_ALL}")
                        try:
                            # JOIN_MATCH ACK
                            ack_counter_holder[0] = (ack_counter_holder[0] + 1) & 0xFFFF
                            counter = ack_counter_holder[0]
                            content = struct.pack("<H", counter)
                            padded  = await build_padded(content)
                            body    = await tea_cbc_encrypt(padded, udp_key_b)
                            k2 = udp_key_b[0]; v80b = ((k2 << 8) | k2) & 0xFFFF
                            hdr = await encode_header(layout_nr, 0, 2, 0, 1, len(body), k2, v80b)
                            jm_ack = bytearray([0x64, 0x00]) + hdr + body
                            jm_ack[1] = await crc7_buff(0, bytes(jm_ack[2:])) & 0x7F
                            await loop.sock_sendto(sock, bytes(jm_ack), (ip, port))
                            _log(cmd, f"{Style.BRIGHT}{Fore.GREEN}[JOIN_MATCH ACK] sent counter={counter}{Style.RESET_ALL}")
                            join_match_received = True

                            await asyncio.sleep(0.3)

                            # Start periodic tasks
                            sync_stop = asyncio.Event()
                            sync_task = asyncio.create_task(
                                _sync_time_sender(sock, ip, port, udp_key_b, layout_nr, sync_stop)
                            )
                            _log(cmd, f"{Style.BRIGHT}{Fore.CYAN}[SYNC_TIME] started (1s, cmd=2000){Style.RESET_ALL}")

                            ack_stop = asyncio.Event()
                            ack_task = asyncio.create_task(
                                _ack_sender(sock, ip, port, udp_key_b, layout_nr,
                                            ack_stop, ack_counter_holder, interval=_ACK_INTERVAL)
                            )
                            _log(cmd, f"{Style.BRIGHT}{Fore.GREEN}[ACK SENDER] started (1s, cmd=2){Style.RESET_ALL}")

                            state_stop = asyncio.Event()
                            state_task = asyncio.create_task(
                                _state_sync_sender(sock, ip, port, udp_key_b, state_stop,
                                                   interval=_TEST_UDP_INTERVAL)
                            )
                            _log(cmd, f"{Style.BRIGHT}{Fore.MAGENTA}[STATE_SYNC] started (10s, cmd=2001){Style.RESET_ALL}")

                            emote_stop = asyncio.Event()
                            emote_task = asyncio.create_task(
                                _emote_sender(sock, ip, port, emote_stop,
                                              interval=_TEST_EMOTE_INTERVAL)
                            )
                            _log(cmd, f"{Style.BRIGHT}{Fore.YELLOW}[EMOTE] started (10s, cmd=371){Style.RESET_ALL}")

                        except Exception as e:
                            print(f"{Style.BRIGHT}{Fore.RED}[JOIN_MATCH ERROR] {e}{Style.RESET_ALL}")
                            traceback.print_exc()

                    elif cmd == 2:
                        try:
                            ack_counter_holder[0] = (ack_counter_holder[0] + 1) & 0xFFFF
                            counter = ack_counter_holder[0]
                            mk = _ACK_MSG_KEYS[counter % len(_ACK_MSG_KEYS)]
                            content = struct.pack("<H", counter)
                            ack_pkt = await build_packet(mk, layout_nr, 0, 2, 0, 1,
                                                          content, udp_key_b)
                            await loop.sock_sendto(sock, ack_pkt, (ip, port))
                            _log(cmd, f"{Style.BRIGHT}{Fore.GREEN}[ACK] replied counter={counter}{Style.RESET_ALL}")
                        except Exception as e:
                            print(f"{Style.BRIGHT}{Fore.RED}[ACK ERROR] {e}{Style.RESET_ALL}")

            except asyncio.TimeoutError:
                if state == "waiting_for_ack":
                    last_hello_time = 0  # force retx
                else:
                    print(f"{Style.BRIGHT}{Fore.YELLOW}[TIMEOUT] 30s no data — state={state}{Style.RESET_ALL}")
                continue
            except Exception as e:
                print(f"{Style.BRIGHT}{Fore.RED}[MONITOR ERROR] {e}{Style.RESET_ALL}")
                traceback.print_exc()
                break

    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[MATCH SERVER ERROR] {e}{Style.RESET_ALL}")
        traceback.print_exc()

    finally:
        try:
            for ev in (ping_stop, sync_stop, ack_stop, state_stop, emote_stop):
                if ev is not None: ev.set()
            for t in (ping_task, sync_task, ack_task, state_task, emote_task):
                if t is not None:
                    t.cancel()
                    try: await t
                    except (asyncio.CancelledError, Exception): pass
        except Exception:
            pass
        try:
            if sock is not None: sock.close()
        except Exception:
            pass
        print(f"{Style.BRIGHT}{Fore.CYAN}[UDP] socket closed{Style.RESET_ALL}")

async def tcp_online(ip, port, auth_token, key, iv, region, reconnect_delay=0.1):
    global online_writer, owner_uid, group_id, team_owner_uid, team_chat_code, last_room_id, ghost_team_owner, ghost_team_id, last_status_packet
    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Connecting Tcp Online On Region: {region}")
    key = bytes.fromhex(key)
    iv = bytes.fromhex(iv)
    while True:
        try:
            reader, online_writer = await asyncio.open_connection(ip, int(port))
            bytes_payload = bytes.fromhex(auth_token)
            await send_packet(bytes_payload, 'online')
            
            # Heartbeat task for online connection - only header
            async def online_heartbeat():
                while True:
                    try:
                        await asyncio.sleep(30)
                        if online_writer:
                            # Only 4 bytes header: 0219
                            online_writer.write(bytes.fromhex("0219"))
                            await online_writer.drain()
                            print(f"{Style.BRIGHT}{Fore.CYAN}[ONLINE HB] {Fore.GREEN}0219 sent")
                    except Exception as e:
                        print(f"{Style.BRIGHT}{Fore.RED}[ONLINE HB ERROR] {e}")
                        break
            
            heartbeat_task = asyncio.create_task(online_heartbeat())
            
            while True:
                data = await reader.read(9999)
                if not data: 
                    print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE ERROR] Connection Closed By The Server!")
                    break
                
                if data.hex():
                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Response Received: {data.hex()}")
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    json_data = json.loads(decoded_json)
                    pretty_json = json.dumps(json_data, indent=2, default=str)
                    print(pretty_json)

                # ═══════════════════════════════════════════════════
                #  ★ 0300 HANDLER — Match server OR Social island
                # ═══════════════════════════════════════════════════
                if data.hex().startswith("0300"):
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    if decoded_json:
                        json_data = json.loads(decoded_json)
                        
                        # ─── Check for MATCH SERVER (5.1, 5.2, 5.3, 5.4 all present) ───
                        match_server_detected = False
                        try:
                            f5 = json_data.get("5", {}).get("data", {})
                            if isinstance(f5, dict):
                                has_1 = "1" in f5
                                has_2 = "2" in f5
                                has_3 = "3" in f5
                                has_4 = "4" in f5
                                if has_1 and has_2 and has_3 and has_4:
                                    sa = f5["2"].get("data", "")
                                    if sa and ":" in str(sa) and len(str(sa)) < 60:
                                        match_server_detected = True
                                        print(f"{Style.BRIGHT}{Fore.YELLOW}[TCP ONLINE] ★ 0300 MATCH SERVER — spawning handler task...{Style.RESET_ALL}")
                                        asyncio.create_task(
                                            udp_task(json_data, key, iv, region)
                                        )
                        except Exception as e:
                            print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE MATCH DETECT ERROR] {e}")
                        
                if data.hex().startswith("0600"):
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    json_data = json.loads(decoded_json)
                    try:
                        if "2" in json_data and "4" in json_data and "5" in json_data:
                            field_data = json_data.get("5", {}).get("data", {})
                            if "1" in field_data:
                                target_uid = field_data.get("1", {}).get("data", 0)
                                if "7" in field_data:
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Uid Found For Accept Friend Request! ~ {target_uid}")
                                    if _accept_friend_request:
                                        accept_response = await accept_friend_request(target_uid)
                                        _target_name = accept_response.get(3, "Unknown")
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Friend Request Successfully Accepted Of ~ {Fore.CYAN}{_target_name} ({target_uid})")
                                else:
                                    print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE] Deleted Me From Friend List! ~ {target_uid}")
                    except Exception as e:
                        print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE ERROR] {e}")
                        
                if data.hex().startswith("0500"):
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    json_data = json.loads(decoded_json)
                    try:
                        if "5" in json_data:
                            if str(json_data.get("5", {}).get("data", {}).get("1", {}).get("data", None)).isdigit() and len(str(json_data.get("5", {}).get("data", {}).get("1", {}).get("data", None))) > 7:
                                owner_uid = json_data.get("5", {}).get("data", {}).get("1", {}).get("data", None)
                                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Uid Found For Accept invite! ~ {owner_uid}")
                            else:
                                owner_uid = None
                            if len(str(json_data.get("5", {}).get("data", {}).get("8", {}).get("data", None))) == 30:
                                group_id  = json_data.get("5", {}).get("data", {}).get("8", {}).get("data", None)
                                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Group Id Found For Accept invite! ~ {group_id}")
                            else:
                                group_id  = None
                    except Exception as e:
                        print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE ERROR] {e}")
                    if owner_uid and group_id:
                        
                        packet = reject_invite(owner_uid, name_text, key, iv)
                        await send_packet(packet, 'online')
                        
                        await asyncio.sleep(0.2)
                        
                        packet = accept_invite(owner_uid, group_id, key, iv)
                        await send_packet(packet, 'online')
                        
                        owner_uid, group_id = None, None 

                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Invite Accepted Successfully!")

                # Auth Team Chat + Ghost (FIXED)
                if data.hex().startswith("0500"):
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    if decoded_json:
                        json_data = json.loads(decoded_json)

                        try:
                            if "5" in json_data:
                                field5 = json_data["5"].get("data", {})

                                # Initialize variables
                                team_owner_uid = None
                                ghost_team_owner = None
                                team_chat_code = None
                                ghost_team_id = None

                                # Team Owner UID - usually in field 1
                                if "1" in field5:
                                    team_owner_uid = field5["1"].get("data")
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Team Owner UID: {team_owner_uid}")
    
                                    # Check if this is our own team (we are the owner)
                                    if team_owner_uid == account_id:
                                        # For our own team, ghost owner might be in field 3 (if it's a dict)
                                        if "3" in field5:
                                            # Check if field 3 is a dict (nested data)
                                            if isinstance(field5["3"], dict):
                                                field3_data = field5["3"].get("data", {})
                                                if isinstance(field3_data, dict) and "1" in field3_data:
                                                    ghost_team_owner = field3_data["1"].get("data")
                                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Ghost Team Owner (from field 3): {ghost_team_owner}")
                                            # If field 3 is not a dict, skip it
                                    else:
                                        # For other's team, ghost owner is the team owner
                                        ghost_team_owner = team_owner_uid
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Ghost Team Owner (from field 1): {ghost_team_owner}")

                                # Team Chat Code - usually in field 17
                                if "17" in field5:
                                    team_chat_code = field5["17"].get("data")
                                    if team_chat_code:
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Team Chat Code: {team_chat_code}")
                                        
                                # Ghost Team ID - usually in field 31 (nested inside field 3)
                                if "3" in field5:
                                    # Check if field 3 is a dict (nested data)
                                    if isinstance(field5["3"], dict):
                                        field3_data = field5["3"].get("data", {})
                                        if isinstance(field3_data, dict):
                                            # Ghost ID might be in field 31 inside field 3
                                            if "31" in field3_data:
                                                ghost_team_id = field3_data["31"].get("data")
                                                if ghost_team_id:
                                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Ghost Team ID (from field 3.31): {ghost_team_id}")
                            
                                            # Alternative: field 31 directly in field5
                                            if not ghost_team_id and "31" in field5:
                                                ghost_team_id = field5["31"].get("data")
                                                if ghost_team_id:
                                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Ghost Team ID (from field 31): {ghost_team_id}")
                                                        
                                    # Debug prints
                                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.YELLOW}--- DEBUG ---{Style.RESET_ALL}")
                                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.YELLOW}Team Owner UID: {team_owner_uid}{Style.RESET_ALL}")
                                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.YELLOW}Ghost Team Owner: {ghost_team_owner}{Style.RESET_ALL}")
                                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.YELLOW}Team Chat Code: {team_chat_code}{Style.RESET_ALL}")
                                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.YELLOW}Ghost Team ID: {ghost_team_id}{Style.RESET_ALL}")
                                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.YELLOW}Account ID: {account_id}{Style.RESET_ALL}")

                                # Ghost Join - FIXED: Check if ghost_team_owner is different from account_id
                                if ghost_team_owner and ghost_team_id and not is_sending_team_code_emote:
                                    # Only join ghost if owner is different from our account
                                    if ghost_team_owner != account_id and auto_ghost_on_leave:
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Attempting Ghost Join...{Style.RESET_ALL}")
                                        name = f"[00FF00]{bot_owner}"
                                        ghost_packet = join_ghost(ghost_team_owner, ghost_team_id, name, key, iv)
                                        await send_packet(ghost_packet, 'online')
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Ghost Join Sent!{Style.RESET_ALL}")
                                    else:
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.YELLOW}Skipping Ghost Join - Owner is our account{Style.RESET_ALL}")
                                else:
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.YELLOW}Ghost Join conditions not met: ghost_team_owner={ghost_team_owner}, ghost_team_id={ghost_team_id}, is_sending_team_code_emote={is_sending_team_code_emote}{Style.RESET_ALL}")

                                # Team Chat Authorization
                                if team_owner_uid and team_chat_code and not is_sending_team_code_emote:
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Authorizing Team Chat...{Style.RESET_ALL}")
                                    team_chat_packet = auth_team_chat(team_owner_uid, team_chat_code, key, iv)
                                    await send_packet(team_chat_packet, 'chat')
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Team Chat Authorization Sent!{Style.RESET_ALL}")

                                    # Welcome Message
                                    await asyncio.sleep(1)
                                    msg = "[00FF00]Welcome!"
                                    packet = send_message(account_id, team_owner_uid, 0, msg, key, iv)
                                    await send_packet(packet, 'chat')
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Welcome Message Sent!{Style.RESET_ALL}")
                                    team_owner_uid, team_chat_code = None, None

                        except Exception as e:
                            print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE TEAM EXTRACT ERROR] {e}{Style.RESET_ALL}")
                            # Print the problematic data for debugging
                            try:
                                print(f"{Style.BRIGHT}{Fore.YELLOW}[DEBUG] Field5 data: {json.dumps(field5, indent=2, default=str)[:500]}{Style.RESET_ALL}")
                            except:
                                pass
                
                if data.hex().startswith("0500"):
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    if decoded_json:
                        json_data = json.loads(decoded_json)
        
                        try:
                            if "5" in json_data:
                                field5 = json_data["5"].get("data", {})
                
                                # Check if this is a join request (has "1" = uid, "3" = name, "4" = level, "5" = badge)
                                if "1" in field5 and "3" in field5 and "4" in field5 and "5" in field5:
                                    target_uid = field5["1"].get("data")
                                    _target_name = field5["3"].get("data", "Unknown")
                    
                                    if str(target_uid).isdigit() and len(str(target_uid)) > 7 and len(str(target_uid)) < 15:
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Join request from: {_target_name} (UID: {target_uid}")
                        
                                        # Auto accept
                                        packet = accept_join_request(account_id, target_uid, key, iv)
                                        await send_packet(packet, 'online')
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Join request accepted from {_target_name} (UID: {target_uid})")
                        
                        except Exception as e:
                            print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE JOIN ACCEPT ERROR] {e}")

                if data.hex().startswith("0500"):
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    if decoded_json:
                        json_data = json.loads(decoded_json)
        
                        try:
                            if "5" in json_data:
                                field5 = json_data["5"].get("data", {})
                
                                if "1" in field5 and "2" in field5:
                                    # Check if field 2 is a dict (nested data)
                                    if isinstance(field5["2"], dict):
                                        field2_data = field5["2"].get("data", {})
                        
                                        # Extract target_uid from field 5.1
                                        target_uid = field5["1"].get("data")
                        
                                        # Extract group_id from field 5.7 (string format)
                                        group_id = None
                        
                                        # Primary: Check field 5.7 for group_id
                                        if "7" in field5:
                                            group_id = field5["7"].get("data")
                                            if group_id:
                                                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Found group_id in field 7: {group_id}")
                        
                                        # Secondary: Check field 5.2.1 for group_id
                                        if not group_id and isinstance(field2_data, dict):
                                            if "1" in field2_data:
                                                group_id = field2_data["1"].get("data")
                                                if group_id:
                                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Found group_id in field 2.1: {group_id}")
                        
                                        # Tertiary: Check field 5.2.7
                                        if not group_id and isinstance(field2_data, dict):
                                            if "7" in field2_data:
                                                group_id = field2_data["7"].get("data")
                                                if group_id:
                                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Found group_id in field 2.7: {group_id}")
                        
                                        # Check if this is a valid invite request
                                        if target_uid and group_id:
                                            if str(target_uid).isdigit() and len(str(target_uid)) > 7:
                                                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Group join from UID: {target_uid}, Group ID: {group_id}")
                                
                                                if join_on_team_request_accept:
                                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Accepting group join...")
                                    
                                                    # Send accept invite with group_id
                                                    packet = accept_invite(target_uid, group_id, key, iv)
                                                    await send_packet(packet, 'online')
                                    
                                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Group Join accepted from {target_uid}")
                        except Exception as e:
                            print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE TEAM JOIN ERROR] {e}")
                        
                if data.hex().startswith("0e00"):
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    if decoded_json:
                        json_data = json.loads(decoded_json)
        
                        # Check for room join request
                        try:
                            if "5" in json_data:
                                field5 = json_data["5"].get("data", {})
                
                                # Check if this is a room join request
                                # Field 5 has "1" (uid) and "2" (name)
                                if "1" in field5 and "2" in field5:
                                    target_uid = field5["1"].get("data")
                                    _target_name = field5["2"].get("data", "Unknown")
                    
                                    if str(target_uid).isdigit() and len(str(target_uid)) > 7 and len(str(target_uid)) < 15 and len(str(_target_name)) < 13:
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Room join request from: {_target_name} (UID: {target_uid})")
                        
                                        # Auto accept room join
                                        packet = accept_room_join(target_uid, key, iv)
                                        await send_packet(packet, 'online')
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Room join accepted from {_target_name} (UID: {target_uid})")
                        
                        except Exception as e:
                            print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE ROOM JOIN ERROR] {e}")
                
                # Accept Room Invite 
                if data.hex().startswith("0e00"):
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    if decoded_json:
                        json_data = json.loads(decoded_json)

                        # Check for room invite response
                        try:
                            if "5" in json_data:
                                field5 = json_data["5"].get("data", {})
                
                                # Check if this is a room invite (has "1" and "2")
                                if "1" in field5 and "2" in field5:
                                    room_id = field5["1"].get("data")  # Room ID
                    
                                    # Extract target_uid from nested field 5.2.1
                                    target_uid = None
                                    if "2" in field5 and isinstance(field5["2"], (int, dict)):
                                        if isinstance(field5["2"], (dict)):
                                            if str(field5["2"]["data"]).isdigit():
                                                print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE ROOM INVITE] Field 2 Is Int!")
                                            else:
                                                sub_field2 = field5["2"].get("data", {})
                                                if "1" in sub_field2:
                                                    target_uid = sub_field2["1"].get("data")
                    
                                    if len(str(room_id)) < 12 and len(str(room_id)) > 8 and str(target_uid).isdigit() and len(str(target_uid)) > 7 and len(str(target_uid)) < 15:
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Room invite response - Room: {room_id}, Invites From: {target_uid}")
                        
                                        # Auto accept room invite
                                        packet = accept_room_invite_or_join_room(room_id, None, key, iv)
                                        await send_packet(packet, 'online')
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Room invite accepted! (Room: {room_id})")
                        
                        except Exception as e:
                            print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE ROOM INVITE ERROR] {e}")
                
                # room chat authorization 
                if data.hex().startswith('0e00'):
                    data_hex = data.hex()[10:]
                    json_response = decode_packet(data_hex)
    
                    json_data = json.loads(json_response)
    
                    room_chat_id = None
                    room_id = None
    
                    try:
                        # Try to find room_id from different possible locations
                        if "5" in json_data:
                            field5 = json_data["5"].get("data", {})
            
                            # Method 1: Direct room_id in field 5.1
                            if "1" in field5:
                                room_id_value = field5["1"].get("data")
                                if isinstance(room_id_value, int) and len(str(room_id_value)) <= 12:
                                    room_id = room_id_value
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Room ID (direct): {room_id}")
            
                            # Method 2: Room ID nested inside field 5.2 (room info)
                            if not room_id and "2" in field5:
                                field2 = field5["2"].get("data", {})
                                if isinstance(field2, dict) and "1" in field2:
                                    room_id_value = field2["1"].get("data")
                                    if isinstance(room_id_value, int) and len(str(room_id_value)) <= 12:
                                        room_id = room_id_value
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Room ID (nested): {room_id}")
            
                            # Method 3: Room ID in field 5.1.1 (when 5.1 is a nested object)
                            if not room_id and "1" in field5:
                                field1 = field5["1"].get("data", {})
                                if isinstance(field1, dict) and "1" in field1:
                                    room_id_value = field1["1"].get("data")
                                    if isinstance(room_id_value, int) and len(str(room_id_value)) <= 12:
                                        room_id = room_id_value
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Room ID (nested 2): {room_id}")
            
                            # Get room_chat_id from field 5.36
                            if "36" in field5:
                                room_chat_id = field5["36"].get("data")
                                if room_chat_id:
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Room Chat ID: {room_chat_id}")
            
                            # Alternative: room_chat_id might be inside field 5.2
                            if not room_chat_id and "2" in field5:
                                field2 = field5["2"].get("data", {})
                                if isinstance(field2, dict) and "36" in field2:
                                    room_chat_id = field2["36"].get("data")
                                    if room_chat_id:
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Room Chat ID (nested): {room_chat_id}")
            
                            # Alternative: room_chat_id might be field 5.1.36
                            if not room_chat_id and "1" in field5:
                                field1 = field5["1"].get("data", {})
                                if isinstance(field1, dict) and "36" in field1:
                                    room_chat_id = field1["36"].get("data")
                                    if room_chat_id:
                                        print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Room Chat ID (nested 2): {room_chat_id}")
            
                            # If we have both room_id and room_chat_id, authorize
                            if room_id:
                                last_room_id = room_id 
                            
                            if room_id and room_chat_id:
                                room_chat_packet = auth_room_chat(room_id, room_chat_id, key, iv)
                                await send_packet(room_chat_packet, 'chat')
                                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Room Chat Authorization Sent Successfully!")
                
                                await asyncio.sleep(0.5)
                
                                # Send welcome message
                                msg = "[00FF00]Welcome!"
                                packet = send_message(account_id, room_id, 3, msg, key, iv)
                                await send_packet(packet, 'chat')
                                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Room Chat Welcome Message Sent!!")
                                room_chat_id = None 
                            else:
                                if not room_id:
                                    print(f"{Style.BRIGHT}{Fore.YELLOW}[TCP ONLINE] Room ID not found in response")
                                if not room_chat_id:
                                    print(f"{Style.BRIGHT}{Fore.YELLOW}[TCP ONLINE] Room Chat ID not found in response")
                    
                    except Exception as e:
                        print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE ROOM CHAT ERROR] {e}")
                        traceback.print_exc()
                
                if data.hex().startswith("0c00"):
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    json_data = json.loads(decoded_json)
                    try:
                        if "5" in json_data:
                            field_data = json_data.get("5", {}).get("data", {})
                            if "2" in field_data and "1" in field_data:
                                target_clan_id = field_data.get("2", {}).get("data", 0)
                                clan_owner_uid = field_data.get("1", {}).get("data", 0)
                                if "3" in field_data:
                                    target_clan_name = field_data.get("3", {}).get("data", 0)
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.MAGENTA}Clan Id Found For Join Clan! ~ {target_clan_id} ({target_clan_name}) ~ Owner - {clan_owner_uid}")

                                    if _accept_clan_request:
                                        accept_response = await accept_clan_request(clan_owner_uid, target_clan_id)
                                        if accept_response:
                                            clan_chat_code = accept_response.get(1, None)
                                            clan_chat_packet = auth_clan_chat(target_clan_id, clan_chat_code, key, iv)
                                            await send_packet(clan_chat_packet, 'chat')
                                            print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] {Fore.GREEN}Clan Request Successfully Accepted Of ~ {Fore.CYAN}{target_clan_name} ({clan_chat_code})")
                                else:
                                    print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE] Kicked Me From Clan! ~ {target_clan_id}")
                    except Exception as e:
                        print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE ERROR] {e}")
                
                if data.hex().startswith('0f00'):
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    json_data = json.loads(decoded_json)
                    last_status_packet = json_data 
                
        except Exception as e:
            print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE ERROR] {e}")
            online_writer = None 
        await asyncio.sleep(reconnect_delay)

async def tcp_chat(ip, port, auth_token, key, iv, ready_event, region, clan_id=None, clan_key=None, reconnect_delay=0.1):
    global chat_writer, is_sending_team_code_emote, last_status_packet, is_craftland 
    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.MAGENTA}Connecting Tcp Chat On Region: {region}")
    key = bytes.fromhex(key)
    iv = bytes.fromhex(iv)
    while True:
        try:
            reader, chat_writer = await asyncio.open_connection(ip, int(port))
            bytes_payload = bytes.fromhex(auth_token)
            await send_packet(bytes_payload, 'chat')
            ready_event.set()
            
            # Heartbeat task for chat connection - only header
            async def chat_heartbeat():
                while True:
                    try:
                        await asyncio.sleep(30)
                        if chat_writer:
                            # Only 4 bytes header: 0219
                            chat_writer.write(bytes.fromhex("0219"))
                            await chat_writer.drain()
                            print(f"{Style.BRIGHT}{Fore.CYAN}[CHAT HB] {Fore.GREEN}0219 sent")
                    except Exception as e:
                        print(f"{Style.BRIGHT}{Fore.RED}[CHAT HB ERROR] {e}")
                        break
            
            heartbeat_task = asyncio.create_task(chat_heartbeat())
            
            if clan_id and clan_key:
                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.YELLOW}Bot Connecting With Clan Chat!")
                clan_chat_packet = auth_clan_chat(clan_id, clan_key, key, iv)
                await send_packet(clan_chat_packet, 'chat')
                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.GREEN}Bot Connected With Clan Chat!")
            if auth_world_chat:
                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.YELLOW}Bot Connecting With World Chat!")
                global_chat_packet = auth_global_chat(5, key, iv)
                await send_packet(global_chat_packet, 'chat')
                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.GREEN}Bot Connected With World Chat!")
            while True:
                data = await reader.read(9999)
                if not data: 
                    print(f"{Style.BRIGHT}{Fore.RED}[TCP CHAT ERROR] Connection Closed By The Server!")
                    break
                if data.hex().startswith("120000"):
                    #print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.MAGENTA}Response Received: {data.hex()}")
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    if decoded_json:
                        try:
                            json_data = json.loads(decoded_json)
                            #print(json.dumps(json_data, indent=2, default=str))
            
                            # Initialize variables with default values
                            chat_type = 0
                            uid = 0
                            name = "Unknown"
                            chat_id = None
                            message = ""
                            input_json = ""
                            input_message = ""
            
                            # Safely extract data using get() with defaults
                            if "5" in json_data and isinstance(json_data["5"], dict):
                                outer = json_data["5"].get("data", {})
                                if isinstance(outer, dict):
                                    chat_type = outer.get("3", {}).get("data", 0) if isinstance(outer.get("3"), dict) else 0
                                    uid = outer.get("1", {}).get("data", 0) if isinstance(outer.get("1"), dict) else 0
                    
                                    # Get name from nested 9.1
                                    if "9" in outer and isinstance(outer["9"], dict):
                                        sender_data = outer["9"].get("data", {})
                                        if isinstance(sender_data, dict):
                                            target_name = sender_data.get("1", {}).get("data", "Unknown") if isinstance(sender_data.get("1"), dict) else "Unknown"
                    
                                    # Get chat_id
                                    if chat_type == 2:
                                        chat_id = uid
                                    elif "2" in outer and isinstance(outer["2"], dict):
                                        chat_id = outer["2"].get("data", None)
                    
                                    # Get message
                                    if "4" in outer and isinstance(outer["4"], dict):
                                        message = outer["4"].get("data", "")
                    
                                    # Get JSON
                                    if "8" in outer and isinstance(outer["8"], dict):
                                        input_json = outer["8"].get("data", "")
                    
                                    # Get input message (lowercase)
                                    if message:
                                        if isinstance(message, str):
                                            input_message = message.lower()
                                        else:
                                            input_message = str(message).lower()
                    
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.GREEN}Chat Response Received!")
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.MAGENTA}Chat Type: {chat_type}")
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.MAGENTA}Uid: {uid}")
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.MAGENTA}Name: {target_name}")
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.MAGENTA}Chat Id: {chat_id}")
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.MAGENTA}Message: {message}")
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.MAGENTA}Json: {input_json}")
                                    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.MAGENTA}Input Message: {input_message}")
            
                        except json.JSONDecodeError:
                            print(f"{Style.BRIGHT}{Fore.YELLOW}[TCP CHAT] Received non-JSON data, skipping...{Style.RESET_ALL}")
                            continue
                        except Exception as e:
                            print(f"{Style.BRIGHT}{Fore.RED}[TCP CHAT EXTRACT ERROR] {e}{Style.RESET_ALL}")
                            continue
                    
                    # COPY AND SEND ANY JSON
                    if input_json:
                        if uid != account_id:
                            if not input_json == 'DefaultMessageWithKey':
                                print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.YELLOW}uid - {uid} & account_id - {account_id}!")
                                packet = send_json(account_id, chat_id, chat_type, input_json, key, iv)
                                await send_packet(packet, 'chat')
                        else:
                            print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] {Fore.YELLOW}Skipping Json Copy!")
                    
        except Exception as e:
            print(f"{Style.BRIGHT}{Fore.RED}[TCP CHAT ERROR] {e}")
            chat_writer = None 
        await asyncio.sleep(reconnect_delay)

async def main():
    try:
        global jwt_token, nickname, game_version, release_version, server_url, account_id, clan_id
        uid = 794006
        password = "MARUF"
        game_version, release_version, login_url = await update()
        if uid and password:
            access_token, open_id, platform = await get_access_token_v2(uid, password)
            if access_token and open_id and platform and game_version:
                major_login_payload, login_data_payload = await get_payload(access_token, open_id, platform, game_version)
                if major_login_payload and login_url and release_version:
                    major_login_response = await major_login(major_login_payload, login_url, release_version)
                    account_id = major_login_response.get(1, None) if major_login_response else None
                    print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.YELLOW}Account Id: {account_id}")
                    region = major_login_response.get(2, None) if major_login_response else None
                    print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.YELLOW}Region: {region}")
                    jwt_token = major_login_response.get(8, None) if major_login_response else None
                    print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.GREEN}Jwt Token: {jwt_token}")
                    server_url = major_login_response.get(10, None) if major_login_response else None
                    print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.YELLOW}Server Url: {server_url}")
                    key = major_login_response.get(22, None) if major_login_response else None
                    print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.YELLOW}Key: {key}")
                    iv = major_login_response.get(23, None) if major_login_response else None
                    print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.YELLOW}Iv: {iv}")
                    timestamp = major_login_response.get(21, None) if major_login_response else None
                    print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.GREEN}Timestamp: {timestamp}")
                    if jwt_token and server_url:
                        emote_x = await equip_default_emote()
                        if emote_x:
                            print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.GREEN}Default Emote Successfully Equipped!")
                        login_data_response = await get_login_data(login_data_payload, jwt_token, server_url, release_version)
                        if login_data_response:
                            nickname = login_data_response.get(4, None) if login_data_response else None
                            print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.GREEN}Nickname: {nickname}")
                            chat_server = login_data_response.get(32, None) if login_data_response else None
                            print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.GREEN}Chat Server: {chat_server}")
                            chat_ip, chat_port = chat_server.split(":") if chat_server and ":" in chat_server else (None, None)
                            print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.MAGENTA}Chat Ip: {chat_ip}")
                            print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.MAGENTA}Chat Port: {chat_port}")
                            online_server = login_data_response.get(14, None) if login_data_response else None
                            print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.GREEN}Online Server: {online_server}")
                            online_ip, online_port = online_server.split(":") if online_server and ":" in online_server else (None, None)
                            print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.MAGENTA}Online Ip: {online_ip}")
                            print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.MAGENTA}Online Port: {online_port}")
                            clan_id = login_data_response.get(20, None) if login_data_response else None
                            clan_key = login_data_response.get(55, None) if login_data_response else None
                            print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.YELLOW}Clan Id: {clan_id}")
                            print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.GREEN}Clan Key: {clan_key}")
                            if jwt_token and account_id and key and iv and timestamp:
                                auth_token_online = create_auth_token_online(account_id, jwt_token, timestamp, key, iv)
                                print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.YELLOW}Auth Token For Online: {auth_token_online}")
                                print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.GREEN}Auth Token Online Length: {len(auth_token_online)}")
                                auth_token_chat = create_auth_token_chat(account_id, jwt_token, timestamp, key, iv)
                                print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.YELLOW}Auth Token For Chat: {auth_token_chat}")
                                print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN] {Fore.GREEN}Auth Token Chat Length: {len(auth_token_chat)}")
                                ready_event = asyncio.Event()
                                chat_task = asyncio.create_task(tcp_chat(chat_ip, chat_port, auth_token_chat, key, iv, ready_event, region, clan_id, clan_key))
                                await ready_event.wait()
                                await asyncio.sleep(1)
                                online_task = asyncio.create_task(tcp_online(online_ip, online_port, auth_token_online, key, iv, region))
                                await asyncio.gather(chat_task, online_task)
                        else:
                            print(f"{Style.BRIGHT}{Fore.RED}[MAIN ERROR] Login Data Response Not Received!")
                    else:
                        print(f"{Style.BRIGHT}{Fore.RED}[MAIN ERROR] Jwt Token and Server Url Not Found! Skipping Login Data!")
                else:
                    print(f"{Style.BRIGHT}{Fore.RED}[MAIN ERROR] Payload & Version Not Found! Skipping Major Login!")
            else:
                print(f"{Style.BRIGHT}{Fore.RED}[MAIN ERROR] Access Token & Open Id Not Found! Skipping Payload!")
        else:
            print(f"{Style.BRIGHT}{Fore.RED}[MAIN ERROR] Uid & Password Not Found! Skipping Access Token!")
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[MAIN ERROR] {e}")

async def run():
    while True:
        try:
            print(f"{Style.BRIGHT}{Fore.CYAN}[RUNNER] {Fore.MAGENTA}Starting bot...")
            
            # Run main with 7 hour timeout (JWT token validity period)
            await asyncio.wait_for(main(), timeout=7 * 60 * 60)
            
            # If main completes normally (shouldn't happen in normal operation)
            print(f"{Style.BRIGHT}{Fore.YELLOW}[RUNNER] Bot stopped unexpectedly. Restarting...")
            
        except asyncio.TimeoutError:
            # JWT token expired after 7 hours - restart
            print(f"{Style.BRIGHT}{Fore.YELLOW}[RUNNER] 7 hours passed - JWT token expired. Restarting...")
            
        except asyncio.CancelledError:
            # Handle cancellation gracefully
            print(f"{Style.BRIGHT}{Fore.RED}[RUNNER] Bot cancelled. Shutting down...")
            raise
            
        except Exception as e:
            print(f"{Style.BRIGHT}{Fore.RED}[RUNNER] Error occurred: {e}")
            print(f"{Style.BRIGHT}{Fore.RED}[RUNNER] Traceback: {traceback.format_exc()}")
            print(f"{Style.BRIGHT}{Fore.YELLOW}[RUNNER] Restarting in 3 seconds...")

if __name__ == '__main__':
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print(f"{Style.BRIGHT}{Fore.YELLOW}[RUNNER] Shutting down gracefully...")
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[RUNNER] Fatal error: {e}")