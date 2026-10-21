import aiohttp, asyncio, json, time, traceback, pytz, socket, struct, os, uuid, sys, argparse
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

SKIP_UDP_LOG = [0]

# auto matchmaking config
HELLX_vERS = "2.132.7"

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

FIXED_MIDDLE = bytes.fromhex(
    "010102010104424400020300010000040e322e3133322e371432303139313138353235"
    "ca0163736f7665727365612e7374726f6e67686f6c642e66726565666972656d6f6269"
    "6c652e636f6d3b302e302e302e303b33342e3132362e37362e34353b33342e38372e31"
    "37372e31343b33342e38372e3137302e3233303b33352e3138352e3138332e353700"
)
assert len(FIXED_MIDDLE) == 139

DEFAULT_MID = bytes.fromhex("0000000000000000000100000000000100000000010100c8ddf58daae58cdf110200")
DEFAULT_HEX_PART = b"5cd9b3f05ab07bca7bf41f68ad93e21ee17b2c8f8e00e752ce906d9910e8a545"

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
            if hdr.get("sendOption", 0) > 7 or hdr.get("flags", 0) > 7 or hdr.get("length", 0) != len(data) - off:
                continue

            cmd = hdr.get("cmd", 0)
            score = 0
            if cmd in MESSAGE_ID_TO_NAME:
                score += 20
            if hdr.get("sendOption") == 0:
                score += 10
            if hdr.get("flags") in (0, 1):
                score += 3
            score += len(layout)
            if crc_ok:
                score += 5

            cand = {
                "k": k, "layout": layout, "sendOption": hdr.get("sendOption"),
                "cmd": cmd, "flags": hdr.get("flags"), "orderId": hdr.get("orderId"),
                "length": hdr.get("length"), "body_off": off, "crc_ok": crc_ok, "_score": score,
            }
            if best is None or cand["_score"] > best["_score"]:
                best = cand

    return best

async def build_packet(msg_key, layout, send_option, cmd, order_id, flags, content, key, encrypted=True):
    k = key[0]
    v80 = ((k << 8) | k) & 0xFFFF

    if encrypted:
        padded = await build_padded(content)
        body = await tea_cbc_encrypt(padded, key)
    else:
        body = content

    hdr = bytearray([msg_key, 0x00])
    for code in layout:
        value = {0: send_option, 1: cmd, 2: order_id, 3: flags, 4: len(body)}[code]
        if _FIELD_SIZES[code] == 1:
            hdr.append((value & 0xFF) ^ k)
        else:
            v = ((value & 0xFFFF) ^ v80) & 0xFFFF
            hdr.append(v & 0xFF)
            hdr.append((v >> 8) & 0xFF)

    packet = bytearray(hdr + body)
    packet[1] = await crc7_buff(0, bytes(packet[2:])) & 0x7F
    return bytes(packet)

async def build_hello_packet(account_id, key, layout):
    suffix = "4239"
    msg_key = 0x62
    layout_list = await parse_layout(layout)
    k = key[0]
    v80 = ((k << 8) | k) & 0xFFFF

    text = f"{account_id}_{suffix}"
    tb = text.encode("utf-8")
    content = struct.pack("<I", len(tb)) + tb + b"\x00" * 9
    padded = await build_padded(content)
    body = await tea_cbc_encrypt(padded, key)

    hdr = await encode_header(layout_list, 1, 1, 0, 1, len(body), k, v80)
    packet = bytearray([msg_key, 0x00]) + hdr + body
    packet[1] = await crc7_buff(0, bytes(packet[2:])) & 0x7F
    print(f"[HELLO] text='{text}' body={len(body)} total={len(packet)} crc=0x{packet[1]:02x}", flush=True)
    return bytes(packet).hex()

async def build_prepare_packet(account_id, block_val, udp_key, layout, jwt_token, jwt_len=660):
    jwt_part = jwt_token[:jwt_len].encode() if jwt_token else b""
    content = (await has_ssan_zig(len(jwt_part))) + jwt_part
    return await build_packet(0x63, layout, 2, 447, 0, 1, content, udp_key)

async def build_post_packet(account_id, block_val, host, jwt_token, udp_key, layout,
                            name=b"", mid=None, hex_part=None, msg_key=0x5A):
    if mid is None: mid = DEFAULT_MID
    if hex_part is None: hex_part = DEFAULT_HEX_PART

    c = bytearray()
    c += await uleb_encode(account_id)
    c += await uleb_encode(block_val)
    c += await uleb_encode(1)
    c += await uleb_encode(43)
    c += await uleb_encode(block_val)
    c += await uleb_encode(11)
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
        sig = jwt_parts[2]
        if len(payload_b64) < 830:
            K = 204
            c += b"\xf0\x03"
        else:
            K = 220
            c += b"\x90\x04"
        jwt_sig = (payload_b64[-K:] + "." + sig).encode()
        c += jwt_sig

    content = bytes(c)
    pkt = await build_packet(msg_key, layout, 2, 448, 1, 1, content, udp_key)
    return pkt, content

async def _keepalive_ping(sock, ip, port, udp_key_b, layout_nr, stop_event):
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
            print(f"{Style.BRIGHT}{Fore.CYAN}[KEEPALIVE] PING 0x{pk:02X}  counter={counter}{Style.RESET_ALL}", flush=True)
        except Exception as e:
            print(f"{Style.BRIGHT}{Fore.RED}[KEEPALIVE ERROR] {e}{Style.RESET_ALL}", flush=True)
            break
        i += 1
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=1.0)
        except asyncio.TimeoutError:
            pass

def match_start_packet(key, iv):
    fields = {
        1: 1,
        2: {
            1: bytes.fromhex("0b"),
            2: 43,
            7: {"1": "IDC3", "2": 88, "3": "BD"},
            8: 1,
            9: bytes.fromhex("01090a0b1219202729"),
            11: 1,
            12: {
                1: "080380174151DE80020100000000000000060001000500003050578E0F0000004676251400000000000000000000000000000000000000ff00000000cacfa16d",
                2: 31,
                3: bytes.fromhex("76505e5216060244535500545d50030c00075c520802540b51510d070b59015455085f0b5451510a1b000048755442434c1f0214001817010b4e075379700b5e69456a7678654c41706e5f7870067f0a627e057b750c12054c6c025d63505468675573056068057d417b4d7e044076526354767a0f1b575e5a4416617f18704248004d63626e4207464357425d44631b437a4f420e6b77795a416216440f0814030b4d4676455f42587653660f08027c7d4a785844787c00027f445972450a160f4e4c06611b5b6a60186f0e764b6b5b475b4b7b5c4c1c7c135e494771041105496d7676016066635807667d6e606f506547454b06760247594b50460913004e51025d660876535744407a010d4f550a5a525966545c766d00435f0c120508455e5a63677b7261644e007564455d52066f72555c5456045b070063051202485e707c4d0518487f56795f766d7a7146757008425f7608765703560a110c4d5c4448734b51437b6a7578575c536368614651606d7601455255550a16050244526b4c62094b674f587e17616b56617270636246577062484c01600f14004b6a567a63467109500e787350137f7f417d4367041e62607c5a50040d1a054b645c64497d1e0d717456011e0f5c7c5970717e4a48406d550a4e5a0c1706457c0e7b5d535c627b64404b076f457c0400725700717e0a7b6c600a05"),
                4: "{X\\]",
                6: 14,
                7: bytes.fromhex("147f7156720e161c"),
                8: str(HELLX_vERS),
                9: 2,
                10: 1,
                11: bytes.fromhex("036262535136396d6b4d707756416456324b796f566c534f494241387148342f6d6c53457377414e484357684c513342496c34534731306a4e794c4d7863306a72574b547030794143507973524c67753042716f7238465a476555657a77463177726c386b64773534483776436a74715558493269375a5046684b6e3557314843473357484d61376f486346474a51376b31366344746631665435464351324d47774a66674869646b6e7434685538466a6b4c6a2b733071734345375234556c6c494c7349746951347930526171456934637a596e4f4b31374b426e6c2f4f334a4f643942496b45643664306e52753342486539746672646c545567764f506f7265644b61715837474c517646337a6970366d69784248636b3662737659594971346b3037513054386d49354d466149522b7137324f7674576a664b734e756149424d5979682b5a4178394251582b5574462f7634693272597a366d6f6f41694b664d65493178634649495a49513253777a37412f43696e7a413873785a6c6c77526e757937377757742f4b67507843797a6c6e77653279414f637669316f6d39696d56444b4144554170765647556c39776b4d716639584f477a37426f6745613870507448455642426362716548556c66474653336e6c6457364138314f652b7372616e524a704830735759416866433776344e5777516c414d32314a52524c4c3062415773726e526c4a466339332b44747a494b565a675a6254736b4c756977426a5643524e6856686b4369712f7659524d44464c4e713270673364644a7133632f644f485070512b4d79336550633571616638696b4849382f6c4e504d796b435155644b50426977554b6c4439576636556950486549367a3356737077686f673d3d")
            },
            20: {1: 21},
            21: "a_1477547277882450725"
        }
    }
    proto = create_proto(fields).hex()
    return create_packet(proto, '0319', key, iv)

def lobby_clear_packet(key, iv):
    fields = {1: 2}
    proto = create_proto(fields).hex()
    return create_packet(proto, '0319', key, iv)

def reject_invite(uid, name_text, key, iv):
    fields = {1: 5, 2: {1: int(uid), 2: 1, 3: int(uid), 4: str(name_text)}}
    proto = create_proto(fields).hex()
    return create_packet(proto, '0515', key, iv)

def accept_invite(uid, group_id, key, iv):
    fields = {
        1: 4,
        2: {
            1: int(uid), 3: int(uid), 4: bytes.fromhex("0107090a0b120f19202729"), 8: 1,
            9: {
                1: "08FBA33B0522052002041B0222220007000C00010004000547E265AE1080779546762514110104076fa2e8770e748c3f6a68ed75000000ff08080500cacfa16d",
                2: 235, 3: {14: 80, 11: 86}, 4: "{Y\\R", 6: 13, 7: {2: 4}, 8: f"{game_version}", 9: 2, 10: 1,
                11: "0362625351363749545a306f50416456324b796f566c664b314a522b4c336737676d2f597a6f7064736278516b676d6f3275696a4e5a512f6445356778643942356c6f69644867315574306e34573146634c382b624a69436c61532b305a625070547a32574f302b436d497067325958347a4d38722f526a4a735371764a334a357a69756950676b5a35642b386a7576664367547a7135776e78756b4d5a734d63745544582b666a65325373565833542b6950676c4f31474736526e66383661754e7945786c4a6942316a656d59636452595459496c65612f68757353657a6c6753424c49714e64482f584b7876507a6c74417461756b53746d50414b4c5679544b42337536685146456b7635584962534f626f6f436b4b357a614e523736746e6e6b576176776748446e73426770656c75506e6652644e75714c43547a5553707569355a77425448653937667465354c3432365a71554441724933565a3636687030546234384c756730562b366c514d66636e467143486d33436a356f5549395369776934424758454e33317436786c794932416f6b2f4a322f2b355255574d3645774c497338306a632f55317765745a6b457639524e496f70563275726d38324e4a4858757166346e4d45785a516e6879766268334e5a68554a3431427934574a4b6f44656d367864733873474e444e5874472b4a68466976714d683235536139744b354462336f416871463769416675472f336535304e44744e4e3643796a794a5370633334784765696f6165533544597663782b77634c656e4c373945517475547477716d7a4b4d7575536268514635785272717978796538452f7a5563706a7739534d58654b5268394b685252666b6f4f51785741673d3d"
            },
            10: str(group_id), 11: {"1": "IDC3", "2": 107, "3": "BD"}, 13: "en", 16: "374f5219",
            20: {1: 21}, 23: "a_6534489873065906362",
            24: "https://dl-sg-production.freefiremobile.com/D5A73B5E05EC88BB7181_7104104913_107_1767710870_0",
            27: {1: 2, 2: 4}
        }
    }
    proto = create_proto(fields).hex()
    return create_packet(proto, '0515', key, iv)

def accept_join_request(account_id, target_uid, key, iv):
    fields = {1: 38, 2: {1: int(account_id), 2: int(target_uid), 8: 1}}
    proto = create_proto(fields).hex()
    return create_packet(proto, '0515', key, iv)

def accept_room_join(uid, key, iv):
    fields = {1: 22, 2: {1: int(uid), 2: 1}}
    proto = create_proto(fields).hex()
    return create_packet(proto, '0E15', key, iv)

def accept_room_invite_or_join_room(room_id, room_password, key, iv):
    fields = {
        1: 3,
        2: {
            1: int(room_id), 2: str(room_password) if room_password else None,
            8: {"1": "IDC3", "2": 142, "3": "BD"}, 9: bytes.fromhex("0107090a0b120f19202729"),
            10: 1, 12: bytes.fromhex("ffffffffffffffffff01ffffffffffffffffff01"), 13: 1, 14: 1,
            16: "en", 22: {1: 21}, 24: 1, 25: "a_6534489873065906362"
        }
    }
    proto = create_proto(fields).hex()
    return create_packet(proto, '0E15', key, iv)

def join_ghost(player_id, secret_code, name, key, iv):
    fields = {
        1: 61,
        2: {
            1: int(player_id),
            2: {1: int(player_id), 2: int(account_id), 3: str(name), 5: 1787866961, 6: 53, 7: 25, 8: {2: 1, 3: 1}, 9: 12},
            3: str(secret_code),
        },
    }
    proto = create_proto(fields).hex()
    return create_packet(proto, '0515', key, iv)

def auth_team_chat(owner_uid, chat_code, key, iv):
    fields = {1: 3, 2: {1: owner_uid, 3: "en", 4: str(chat_code)}}
    proto = create_proto(fields).hex()
    return create_packet(proto, '1215', key, iv)

def auth_room_chat(room_id, chat_code, key, iv):
    fields = {1: 3, 2: {1: int(room_id), 2: 3, 3: "en", 4: str(chat_code)}}
    proto = create_proto(fields).hex()
    return create_packet(proto, '1215', key, iv)

def auth_clan_chat(clan_id, clan_key, key, iv):
    fields = {1: 3, 2: {1: int(clan_id), 2: 1, 4: str(clan_key)}}
    proto = create_proto(fields).hex()
    return create_packet(proto, '1201', key, iv)

def auth_global_chat(chat_type, key, iv):
    fields = {1: 3, 2: {2: chat_type, 3: "en"}}
    proto = create_proto(fields).hex()
    return create_packet(proto, '1215', key, iv)

def send_message(uid, chat_id, chat_type, message, key, iv):
    fields = {
        1: int(uid), 2: int(chat_id), 3: chat_type, 4: message, 5: int(datetime.now().timestamp()),
        9: {1: "efbc97efbcb8e38080efbcadefbca1efbcb2efbcb5efbca6", 2: 902037031, 3: 901037021, 4: 312, 5: 827001005, 8: "7X~ARMY", 10: 1, 11: 7, 13: {1: 2}, 14: {1: int(uid), 2: 8, 3: b"\x01\x06\x02"}, 18: {1: int(uid), 3: 6, 4: ""}},
        10: "en",
        13: {1: "https://lh3.googleusercontent.com/a/ACg8ocKUtmlPUNJL7Tk9jW7Unh4Y1UGAPQcVWEV9mxVsPibjK-9ngw=s96-c", 2: 1, 3: 1},
        14: {1: {1: 1, 2: 4, 3: 15, 4: 1, 5: 1789326000, 6: "BD"}}
    }
    proto = create_proto(fields).hex()
    proto = "080112" + encrypt_chat_packet(len(proto) // 2, Tp='Uid') + proto
    return create_packet(proto, '1201', key, iv)

def send_json(uid, chat_id, chat_type, json_str, key, iv):
    show_type = 0 if ("StickerStr" in json_str or "TitleID" in json_str) else 1
    fields = {
        1: int(uid), 2: int(chat_id), 3: chat_type, 5: int(datetime.now().timestamp()), 7: show_type, 8: json_str,
        9: {1: "efbc97efbcb8e38080efbcadefbca1efbcb2efbcb5efbca6", 2: 902037031, 3: 901037021, 4: 312, 5: 827001005, 8: "7X~ARMY", 10: 1, 11: 7, 13: {1: 2}, 14: {1: int(uid), 2: 8, 3: b"\x01\x06\x02"}, 18: {1: int(uid), 3: 6, 4: ""}},
        10: "en",
        13: {1: "https://lh3.googleusercontent.com/a/ACg8ocKUtmlPUNJL7Tk9jW7Unh4Y1UGAPQcVWEV9mxVsPibjK-9ngw=s96-c", 2: 1, 3: 1},
        14: {1: {1: 1, 2: 4, 3: 15, 4: 1, 5: 1789326000, 6: "BD"}}
    }
    proto = create_proto(fields).hex()
    proto = "080112" + encrypt_chat_packet(len(proto) // 2, Tp='Uid') + proto
    return create_packet(proto, '1201', key, iv)

def encrypt_chat_packet(H, Tp):
    e, H = [], int(H)
    while H:
        e.append((H & 0x7F) | (0x80 if H > 0x7F else 0))
        H >>= 7
    return bytes(e).hex() if Tp == 'Uid' else None

def encrypt_aes(hex_data):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(bytes.fromhex(hex_data), AES.block_size)).hex()

def create_vr(N):
    if N < 0: return b''
    H = []
    while True:
        S = N & 0x7F
        N >>= 7
        if N: S |= 0x80
        H.append(S)
        if not N: break
    return bytes(H)

def create_variant(field_number, value):
    return create_vr((field_number << 3) | 0) + create_vr(value)

def create_length(field_number, value):
    encoded_value = value.encode() if isinstance(value, str) else value
    return create_vr((field_number << 3) | 2) + create_vr(len(encoded_value)) + encoded_value

def create_proto(fields):
    try:
        packet = bytearray()
        for field, value in fields.items():
            if isinstance(field, str): field = int(field)
            if isinstance(value, dict):
                nested_packet = create_proto(value)
                packet.extend(create_length(field, nested_packet))
            elif isinstance(value, int):
                packet.extend(create_variant(field, value))
            elif isinstance(value, (str, bytes)):
                packet.extend(create_length(field, value))
        return packet
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[CREATE PROTO ERROR] {e}", flush=True)
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
        if header is None: break
        field_number = header >> 3
        wire_type = header & 0x7
        if wire_type == 0:
            value, offset = decode_varint(data, offset)
            if value is not None: result[field_number] = value
        elif wire_type == 2:
            length, offset = decode_varint(data, offset)
            if length is None: break
            value = data[offset:offset + length]
            offset += length
            try: result[field_number] = value.decode('utf-8')
            except: result[field_number] = value.hex()
        elif wire_type == 1: offset += 8
        elif wire_type == 3: offset += 4
        else: break
    return result

def decode_hex(H):
    R = hex(H)
    F = str(R)[2:]
    return "0" + F if len(F) == 1 else F

def fix_packet(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {'wire_type': result.wire_type}
        if result.wire_type in ("varint", "string", "bytes"):
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = fix_packet(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

def decode_packet(input_text):
    try:
        parsed_results = Parser().parse(input_text)
        return json.dumps(fix_packet(parsed_results))
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[PACKET DECODE ERROR] {e}", flush=True)
        return None

def create_packet(Pk, N, K, V):
    PkEnc = AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(Pk), 16)).hex()
    _ = decode_hex(int(len(PkEnc) // 2))
    if len(_) == 2: HeadEr = N + "000000"
    elif len(_) == 3: HeadEr = N + "00000"
    elif len(_) == 4: HeadEr = N + "0000"
    elif len(_) == 5: HeadEr = N + "000"
    else: HeadEr = N + "0000"
    return bytes.fromhex(HeadEr + _ + PkEnc)

def create_auth_token_online(account_id, jwt_token, timestamp, key, iv):
    try:
        K = bytes.fromhex(key) if isinstance(key, str) else key
        V = bytes.fromhex(iv) if isinstance(iv, str) else iv
        jwt_bytes = jwt_token.encode('utf-8')
        encrypted_packet = AES.new(K, AES.MODE_CBC, V).encrypt(pad(jwt_bytes, AES.block_size))
        header = (
            bytes.fromhex('7319') +
            int(account_id).to_bytes(8, 'big') +
            int(timestamp).to_bytes(4, 'big') +
            b'\x00\x00\x00\x00' +
            len(encrypted_packet).to_bytes(4, 'big')
        )
        return (header + encrypted_packet).hex()
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[AUTH TOKEN ERROR] {e}", flush=True)
        return None

def create_auth_token_chat(account_id, jwt_token, timestamp, key, iv):
    try:
        K = bytes.fromhex(key) if isinstance(key, str) else key
        V = bytes.fromhex(iv) if isinstance(iv, str) else iv
        jwt_bytes = jwt_token.encode('utf-8')
        ct = AES.new(K, AES.MODE_CBC, V).encrypt(pad(jwt_bytes, AES.block_size))
        header = bytes.fromhex('6d19') + int(account_id).to_bytes(8, 'big') + int(timestamp).to_bytes(4, 'big') + len(ct).to_bytes(4, 'big')
        return (header + ct).hex()
    except Exception as e:
        print(f"[AUTH TOKEN ERROR] {e}", flush=True)
        return None

async def equip_default_emote():
    try:
        url = f"{server_url}/ChooseEmote"
        fields = {"6": {"1": 1, "2": 909000001}}
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
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.post(url, headers=headers, data=payload) as response:
                return response.status == 200
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[EMOTE ERROR] {e}", flush=True)
        return None

async def accept_friend_request(uid):
    try:
        url = f"{server_url}/ConfirmFriendRequest"
        fields = {"1": int(uid), "2": int(account_id)}
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
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.post(url, headers=headers, data=payload) as response:
                if response.status == 200:
                    return decode_protobuf(await response.read())
                return None
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[ACCEPT FRIEND ERROR] {e}", flush=True)
        return None

async def accept_clan_request(owner_uid, clan_id):
    try:
        url = f"{server_url}/ApproveJoinClanInvitation"
        fields = {"1": int(owner_uid), "2": int(clan_id)}
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
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.post(url, headers=headers, data=payload) as response:
                if response.status == 200:
                    return decode_protobuf(await response.read())
                return None
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[ACCEPT CLAN ERROR] {e}", flush=True)
        return None

async def update():
    try:
        game_version = "1.132.1"
        print(f"{Style.BRIGHT}{Fore.CYAN}[UPDATE] {Fore.MAGENTA}Game Version: {game_version}", flush=True)
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.post(f'https://version.ggwhitehawk.com/live/ver.php?version={game_version}&lang=en&device=android&channel=android&appsttore=googleplay&region=ME&whitelist_version=1.3.0&whitelist_sp_version=1.0.0&device_name=google%20G011A&device_CPU=ARMv7%20VFPv3%20NEON%20VMH&device_GPU=Adreno%20(TM)%20640&device_mem=1993') as response:
                json_data = json.loads(await response.text())
                release_version = json_data.get('latest_release_version', None)
                login_url = json_data.get('server_url', None)
                game_version = json_data.get('remote_version', game_version)
                print(f"{Style.BRIGHT}{Fore.CYAN}[UPDATE] {Fore.MAGENTA}Release: {release_version}, Login URL: {login_url}", flush=True)
                return game_version, release_version, login_url 
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[UPDATE ERROR] {e}", flush=True)
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
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.post(url, headers=headers, json=data) as response:
                response_text = await response.text()
                if response.status == 200:
                    json_data = json.loads(response_text)
                    if json_data.get('code') == 0:
                        token_data = json_data.get('data', {})
                        return token_data.get('access_token'), token_data.get('open_id'), token_data.get('platform')
                print(f"{Style.BRIGHT}{Fore.RED}[ACCESS TOKEN ERROR] {response_text[:200]}", flush=True)
                return None, None, None
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[ACCESS TOKEN ERROR] {e}", flush=True)
        return None, None, None 

async def get_payload(access_token, open_id, platform, version):
    major_login = {
        "3": str(datetime.now())[:-7], "4": "free fire", "5": 1, "7": f"{version}",
        "8": "Android OS 14 / API-34 (UP1A.231005.007/E135FXXSEEZE2)", "9": "Handheld",
        "11": "CarrierDataNetwork", "12": 1672, "13": 750, "14": "338",
        "15": "ARMv7 VFPv3 NEON | 2002 | 8", "16": 3702, "17": "Mali-G52",
        "18": "OpenGL ES 3.2 v1.r38p1-01bet0-mbs2v41_0.6d20ec041e51b2f2d25dfc265586ebe8",
        "19": f"Google|{uuid.uuid4()}", "21": "en", "22": f"{open_id}", "23": f"{platform}",
        "24": "Handheld", "25": "samsung SM-E135F", "26": "BD", "29": f"{access_token}",
        "30": 1, "42": "Cellular", "57": "7428b253defc164018c604a1ebbfebdf",
        "60": 52037, "61": 5355, "62": 3723, "63": 3, "64": 5483, "65": 52037, "66": 5483, "67": 52037,
        "73": 2, "74": "/data/app/lib/arm", "76": 1, "77": "b8e0cd5e295eee42f5860d3c86e483dd",
        "78": 3, "79": 1, "81": "32", "83": "2019121229", "86": "OpenGLES2", "87": 8191,
        "88": int(platform), "92": 16091, "93": "android", "94": "token", "95": 111107,
        "96": "{\"cur_rate\":null,\"support_etc2\":false}", "97": 1, "98": 1, "99": f"{platform}", "100": f"{platform}",
        "102": "4503454457550c0766", "104": 53792, "105": 1,
        "106": "https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|6b2078db9d22dd98f8e9386a39af8462",
        "107": "c8e41b7a93f02d56e1a94c7b8203f5d1"
    }
    get_login_data = dict(major_login)
    get_login_data["20"] = "104.28.197.151"
    get_login_data["90"] = "Khulna"
    get_login_data["91"] = "D"
    get_login_data["103"] = 1

    encrypted1 = bytes.fromhex(encrypt_aes(create_proto(major_login).hex()))
    encrypted2 = bytes.fromhex(encrypt_aes(create_proto(get_login_data).hex()))
    return encrypted1, encrypted2

async def major_login(payload, login_url, release_version):
    try:
        url = f"{login_url}MajorLogin"
        headers = {
            "Accept": "*/*", "Authorization": "Bearer ", "Content-Type": "application/x-www-form-urlencoded",
            "ReleaseVersion": f"{release_version}", "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "X-GA": "v1 1", "X-GA-SV": str(int(time.time())), "X-Unity-Version": "2018.4.12f1"
        }
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.post(url, headers=headers, data=payload) as response:
                content = await response.read()
                if response.status == 200:
                    PROTO_HEADER_SIZE = 64
                    data = content[PROTO_HEADER_SIZE:] if len(content) > PROTO_HEADER_SIZE else content
                    return decode_protobuf(data)
                return None
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[MAJOR LOGIN ERROR] {e}", flush=True)
        return None

async def get_login_data(payload, jwt_token, server_url, release_version):
    try:
        url = f"{server_url}/GetLoginData"
        headers = {
            "Accept": "*/*", "Authorization": f"Bearer {jwt_token}", "Content-Type": "application/x-www-form-urlencoded",
            "ReleaseVersion": f"{release_version}", "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
            "X-GA": "v1 1", "X-GA-SV": str(int(time.time())), "X-Unity-Version": "2018.4.12f1"
        }
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.post(url, headers=headers, data=payload) as response:
                if response.status == 200:
                    return decode_protobuf(await response.read())
                return None
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[LOGIN DATA ERROR] {e}", flush=True)
        return None 

async def send_packet(packet, packet_type):
    try:
        if packet_type == 'chat' and chat_writer:
            chat_writer.write(packet)
            await chat_writer.drain()
        elif packet_type == 'online' and online_writer:
            online_writer.write(packet)
            await online_writer.drain()
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[PACKET SEND ERROR] {e}", flush=True)

async def udp_task(json_data, key, iv, region, match_ended_signal=None):
    print(f"{Style.BRIGHT}{Fore.GREEN}★ MATCH SERVER DETECTED (3 Level) — HELLO + ACK + PING + PREPARE + POST{Style.RESET_ALL}", flush=True)
    ping_stop = None; ping_task = None; sock = None

    try:
        field5 = json_data.get("5", {}).get("data", {})
        server_addr = field5.get("2", {}).get("data")
        udp_key_hex = field5.get("3", {}).get("data")
        jwt_token = field5.get("4", {}).get("data")
        match_code = field5.get("42", {}).get("data")
        block_val = field5.get("1", {}).get("data")

        if not server_addr or ":" not in str(server_addr):
            if match_ended_signal: match_ended_signal.set()
            return

        ip, port = str(server_addr).split(":")
        port = int(port)
        print(f"{Style.BRIGHT}{Fore.CYAN}[MATCH] 3 Level UDP → {ip}:{port}{Style.RESET_ALL}", flush=True)

        loop = asyncio.get_event_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        sock.connect((ip, port))
        udp_key_b = bytes.fromhex(udp_key_hex)

        try:
            layout_full = [int(c) for c in str(match_code).strip()]
            layout_nr = [c for c in layout_full if c != 2]
        except Exception:
            layout_full = [0, 4, 1, 3, 2]; layout_nr = [0, 4, 1, 3]

        async def build_ping(counter: bytes, msg_key: int):
            k = udp_key_b[0]; v80 = ((k << 8) | k) & 0xFFFF
            content = counter[:5] + b"\x00\x00\x00"
            hdr = await encode_header(layout_nr, 0, 3, 0, 0, len(content), k, v80)
            pkt = bytearray([msg_key, 0x00]) + hdr + content
            pkt[1] = await crc7_buff(0, bytes(pkt[2:])) & 0x7F
            return bytes(pkt)

        hello_hex = await build_hello_packet(account_id, udp_key_b, match_code)
        await loop.sock_sendto(sock, bytes.fromhex(hello_hex), (ip, port))

        saved_ack = None; ping1_counter = None; state = "waiting_for_ack"; join_match_received = False

        while True:
            try:
                data = await asyncio.wait_for(loop.sock_recv(sock, 65535), timeout=30.0)
                if not data: continue
                decoded = _decode_response(data, preferred_layouts=[layout_nr, layout_full])
                if not decoded: continue
                cmd = decoded["cmd"]

                if cmd == 4:
                    print(f"{Style.BRIGHT}{Fore.YELLOW}[BYEBYE] Match ended (3 Level){Style.RESET_ALL}", flush=True)
                    if match_ended_signal: match_ended_signal.set()
                    if ping_stop: ping_stop.set()
                    if ping_task: ping_task.cancel()
                    try: sock.close()
                    except: pass
                    return

                if state == "waiting_for_ack" and cmd == 2:
                    saved_ack = data
                    state = "waiting_for_hello"
                elif state == "waiting_for_hello" and cmd == 1:
                    ack_mirror = bytearray(saved_ack); ack_mirror[0] = 0x6B
                    await loop.sock_sendto(sock, bytes(ack_mirror), (ip, port))
                    atk_body = saved_ack[8:] if len(saved_ack) > 8 else saved_ack[6:]
                    ping1_counter = (atk_body + b"\x00" * 5)[:5]
                    ping1_pkt = await build_ping(ping1_counter, msg_key=0x64)
                    await loop.sock_sendto(sock, ping1_pkt, (ip, port))
                    state = "waiting_for_ping1_reply"
                elif state == "waiting_for_ping1_reply" and cmd == 3:
                    ping2_counter = os.urandom(3) + ping1_counter[3:5]
                    ping2_pkt = await build_ping(ping2_counter, msg_key=0x6D)
                    await loop.sock_sendto(sock, ping2_pkt, (ip, port))
                    state = "waiting_for_ping2_reply"
                elif state == "waiting_for_ping2_reply" and cmd == 3:
                    prepare_pkt = await build_prepare_packet(account_id, block_val, udp_key_b, layout_full, jwt_token)
                    await loop.sock_sendto(sock, prepare_pkt, (ip, port))
                    await asyncio.sleep(0.15)
                    post_pkt, _ = await build_post_packet(account_id, block_val, str(server_addr), jwt_token, udp_key_b, layout_full)
                    await loop.sock_sendto(sock, post_pkt, (ip, port))
                    state = "monitoring"
                    ping_stop = asyncio.Event()
                    ping_task = asyncio.create_task(_keepalive_ping(sock, ip, port, udp_key_b, layout_nr, ping_stop))
                else:
                    if cmd == 100 and not join_match_received:
                        ack_pkt = await build_packet(0x68, layout_nr, 0, 2, None, 1, b"\x02\x00", udp_key_b)
                        await loop.sock_sendto(sock, ack_pkt, (ip, port))
                        join_match_received = True
                    elif cmd == 2:
                        ack_pkt = await build_packet(0x68, layout_nr, 0, 2, None, 1, b"\x01\x00", udp_key_b)
                        await loop.sock_sendto(sock, ack_pkt, (ip, port))
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"{Style.BRIGHT}{Fore.RED}[UDP MONITOR ERROR] {e}{Style.RESET_ALL}", flush=True)
                break
    except Exception as e:
        print(f"{Style.BRIGHT}{Fore.RED}[UDP ERROR] {e}{Style.RESET_ALL}", flush=True)
    finally:
        if ping_stop: ping_stop.set()
        if ping_task: ping_task.cancel()
        if sock:
            try: sock.close()
            except: pass
        if match_ended_signal:
            try: match_ended_signal.set()
            except: pass

async def tcp_online(ip, port, auth_token, key, iv, region, reconnect_delay=0.1):
    global online_writer, owner_uid, group_id, team_owner_uid, team_chat_code, last_room_id, ghost_team_owner, ghost_team_id, last_status_packet
    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP ONLINE] Connecting 3 Level on Region: {region}", flush=True)
    key = bytes.fromhex(key); iv = bytes.fromhex(iv)
    pump_task = None; heartbeat_task = None; match_ended_signal = asyncio.Event()

    while True:
        try:
            reader, online_writer = await asyncio.open_connection(ip, int(port))
            await send_packet(bytes.fromhex(auth_token), 'online')

            async def online_heartbeat():
                while True:
                    try:
                        await asyncio.sleep(30)
                        if online_writer:
                            online_writer.write(bytes.fromhex("0219"))
                            await online_writer.drain()
                    except Exception:
                        break

            heartbeat_task = asyncio.create_task(online_heartbeat())

            # ═══════════════════════════════════════════════════════
            # ★ CONTINUOUS MULTI-MATCH INJECTION PUMP (3 Level)
            # ═══════════════════════════════════════════════════════
            async def matchmaking_pump():
                try:
                    await send_packet(lobby_clear_packet(key, iv), 'online')
                    print(f"{Style.BRIGHT}{Fore.CYAN}[PUMP-L3] Initial lobby clearance sent", flush=True)
                except Exception as e:
                    print(f"[PUMP-L3 INIT ERROR] {e}", flush=True)

                await asyncio.sleep(1.0)
                cycle = 0
                while True:
                    cycle += 1
                    try:
                        await send_packet(lobby_clear_packet(key, iv), 'online')
                        await asyncio.sleep(0.15)
                        await send_packet(match_start_packet(key, iv), 'online')
                        print(f"{Style.BRIGHT}{Fore.CYAN}[PUMP-L3 #{cycle}] {Fore.GREEN}Lone Wolf queue injection triggered! (5.7s loop)", flush=True)
                        await asyncio.sleep(5.7)
                    except asyncio.CancelledError:
                        raise
                    except Exception as e:
                        print(f"[PUMP-L3 ERROR] {e}", flush=True)
                        await asyncio.sleep(2)

            pump_task = asyncio.create_task(matchmaking_pump())

            while True:
                data = await reader.read(9999)
                if not data: break

                if data.hex().startswith("0300"):
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    if decoded_json:
                        json_data = json.loads(decoded_json)
                        f5 = json_data.get("5", {}).get("data", {})
                        if isinstance(f5, dict) and "1" in f5 and "2" in f5 and "3" in f5 and "4" in f5:
                            sa = f5["2"].get("data", "")
                            if sa and ":" in str(sa) and len(str(sa)) < 60:
                                print(f"{Style.BRIGHT}{Fore.YELLOW}[TCP ONLINE-L3] ★ Match server found — spawning UDP task...", flush=True)
                                asyncio.create_task(udp_task(json_data, key, iv, region, match_ended_signal))

                elif data.hex().startswith("0600"):
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    if decoded_json:
                        json_data = json.loads(decoded_json)
                        field_data = json_data.get("5", {}).get("data", {})
                        if "1" in field_data and "7" in field_data:
                            target_uid = field_data.get("1", {}).get("data", 0)
                            if _accept_friend_request:
                                await accept_friend_request(target_uid)

                elif data.hex().startswith("0500"):
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    if decoded_json:
                        json_data = json.loads(decoded_json)
                        f5 = json_data.get("5", {}).get("data", {})
                        if "1" in f5 and "8" in f5:
                            ouid = f5.get("1", {}).get("data")
                            gid = f5.get("8", {}).get("data")
                            if ouid and gid:
                                await send_packet(reject_invite(ouid, name_text, key, iv), 'online')
                                await asyncio.sleep(0.2)
                                await send_packet(accept_invite(ouid, gid, key, iv), 'online')

                elif data.hex().startswith("0e00"):
                    data_hex = data.hex()[10:]
                    decoded_json = decode_packet(data_hex)
                    if decoded_json:
                        json_data = json.loads(decoded_json)
                        f5 = json_data.get("5", {}).get("data", {})
                        if "1" in f5 and "2" in f5:
                            rid = f5.get("1", {}).get("data")
                            await send_packet(accept_room_invite_or_join_room(rid, None, key, iv), 'online')

        except Exception as e:
            print(f"{Style.BRIGHT}{Fore.RED}[TCP ONLINE ERROR] {e}", flush=True)
            online_writer = None

        if pump_task and not pump_task.done(): pump_task.cancel()
        if heartbeat_task and not heartbeat_task.done(): heartbeat_task.cancel()
        match_ended_signal.clear()
        await asyncio.sleep(reconnect_delay)

async def tcp_chat(ip, port, auth_token, key, iv, ready_event, region, clan_id=None, clan_key=None, reconnect_delay=0.1):
    global chat_writer
    print(f"{Style.BRIGHT}{Fore.CYAN}[TCP CHAT] Connecting 3 Level on Region: {region}", flush=True)
    key = bytes.fromhex(key); iv = bytes.fromhex(iv)

    while True:
        try:
            reader, chat_writer = await asyncio.open_connection(ip, int(port))
            await send_packet(bytes.fromhex(auth_token), 'chat')
            ready_event.set()

            async def chat_heartbeat():
                while True:
                    try:
                        await asyncio.sleep(30)
                        if chat_writer:
                            chat_writer.write(bytes.fromhex("0219"))
                            await chat_writer.drain()
                    except Exception:
                        break
            asyncio.create_task(chat_heartbeat())

            while True:
                data = await reader.read(9999)
                if not data: break
        except Exception as e:
            print(f"[TCP CHAT ERROR] {e}", flush=True)
            chat_writer = None
        await asyncio.sleep(reconnect_delay)

async def main(target_uid=None, target_password=None, target_name=None):
    try:
        global jwt_token, nickname, game_version, release_version, server_url, account_id, clan_id, bot_owner
        uid = target_uid if target_uid is not None else 4752927952
        password = target_password if target_password is not None else "PIYASH_KVYDC_BY_STAR_GMR_FL7HG"
        if target_name: bot_owner = target_name

        print(f"[WORKER-L3] Initializing Lone Wolf Pump for UID: {uid}, Name: {bot_owner}", flush=True)
        game_version, release_version, login_url = await update()

        if uid and password:
            access_token, open_id, platform = await get_access_token_v2(uid, password)
            if access_token and open_id and platform and game_version:
                major_login_payload, login_data_payload = await get_payload(access_token, open_id, platform, game_version)
                if major_login_payload and login_url and release_version:
                    major_login_response = await major_login(major_login_payload, login_url, release_version)
                    account_id = major_login_response.get(1) if major_login_response else None
                    region = major_login_response.get(2) if major_login_response else None
                    jwt_token = major_login_response.get(8) if major_login_response else None
                    server_url = major_login_response.get(10) if major_login_response else None
                    key = major_login_response.get(22) if major_login_response else None
                    iv = major_login_response.get(23) if major_login_response else None
                    timestamp = major_login_response.get(21) if major_login_response else None

                    print(f"{Style.BRIGHT}{Fore.CYAN}[MAIN-L3] Account ID: {account_id}, Region: {region}", flush=True)

                    if jwt_token and server_url:
                        await equip_default_emote()
                        login_data_response = await get_login_data(login_data_payload, jwt_token, server_url, release_version)
                        if login_data_response:
                            chat_server = login_data_response.get(32)
                            online_server = login_data_response.get(14)
                            chat_ip, chat_port = chat_server.split(":") if chat_server and ":" in chat_server else (None, None)
                            online_ip, online_port = online_server.split(":") if online_server and ":" in online_server else (None, None)

                            auth_token_online = create_auth_token_online(account_id, jwt_token, timestamp, key, iv)
                            auth_token_chat = create_auth_token_chat(account_id, jwt_token, timestamp, key, iv)

                            ready_event = asyncio.Event()
                            chat_task = asyncio.create_task(tcp_chat(chat_ip, chat_port, auth_token_chat, key, iv, ready_event, region))
                            await ready_event.wait()
                            await asyncio.sleep(1)
                            online_task = asyncio.create_task(tcp_online(online_ip, online_port, auth_token_online, key, iv, region))
                            await asyncio.gather(chat_task, online_task)
    except Exception as e:
        print(f"[MAIN-L3 ERROR] {e}", flush=True)

async def run(uid=None, password=None, name=None):
    while True:
        try:
            print(f"{Style.BRIGHT}{Fore.CYAN}[RUNNER] Starting 3 Level bot pump session...", flush=True)
            await asyncio.wait_for(main(uid, password, name), timeout=7 * 60 * 60)
            print(f"{Style.BRIGHT}{Fore.YELLOW}[RUNNER] Session stopped. Restarting...", flush=True)
        except asyncio.TimeoutError:
            print(f"{Style.BRIGHT}{Fore.YELLOW}[RUNNER] 7 hours passed - JWT expired. Restarting...", flush=True)
        except asyncio.CancelledError:
            print(f"{Style.BRIGHT}{Fore.RED}[RUNNER] Worker cancelled.", flush=True)
            raise
        except Exception as e:
            print(f"[RUNNER-L3 ERROR] {e}", flush=True)
            await asyncio.sleep(3)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="PIYASH LEVEL UP - 3 Level Worker (Match Pump)")
    parser.add_argument("--uid", type=int, default=4752927952, help="Bot Account UID")
    parser.add_argument("--password", type=str, default="PIYASH_KVYDC_BY_STAR_GMR_FL7HG", help="Bot Password")
    parser.add_argument("--name", type=str, default="PIYASH BOT", help="Custom Bot Name")
    args = parser.parse_args()

    try:
        asyncio.run(run(args.uid, args.password, args.name))
    except KeyboardInterrupt:
        print("Shutting down 3 Level Worker...", flush=True)
    except Exception as e:
        print(f"Fatal error: {e}", flush=True)
