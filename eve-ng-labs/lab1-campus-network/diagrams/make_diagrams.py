#!/usr/bin/env python3
"""Generate the Lab 1 diagrams as SVG files.

Usage: python3 make_diagrams.py [output_dir]
Convert to PNG with: rsvg-convert -w 1600 file.svg -o file.png
"""
import html
import os
import sys

W, H = 1600, 900
BG = "#FBFAF7"
INK = "#2C2C2A"
MUTED = "#5F5E5A"
LINE = "#444441"
SANS = "DejaVu Sans, Arial, Helvetica, sans-serif"
MONO = "DejaVu Sans Mono, Consolas, monospace"

STYLES = {
    "net": ("#EEEDFE", "#534AB7", "#26215C", "#534AB7"),
    "host": ("#E1F5EE", "#0F6E56", "#04342C", "#0F6E56"),
    "ext": ("#F1EFE8", "#5F5E5A", "#2C2C2A", "#5F5E5A"),
    "bad": ("#FCEBEB", "#A32D2D", "#501313", "#A32D2D"),
    "good": ("#EAF3DE", "#3B6D11", "#173404", "#3B6D11"),
    "note": ("#FFFFFF", "#B4B2A9", "#2C2C2A", "#5F5E5A"),
    "warn": ("#FAEEDA", "#854F0B", "#412402", "#854F0B"),
    "info": ("#E6F1FB", "#185FA5", "#042C53", "#185FA5"),
}


class Diagram:
    def __init__(self, title, subtitle, desc):
        self.el = []
        self.markers = set()
        self.title = title
        self.desc = desc
        self.rect(0, 0, W, H, BG, None)
        if title:
            self.text(60, 78, title, 42, INK, weight=700)
            self.text(60, 118, subtitle, 22, MUTED)
            self.el.append(f'<line x1="60" y1="142" x2="{W-60}" y2="142" stroke="#D3D1C7" stroke-width="1.5"/>')
            self.text(60, 872, "Lab 1 · Campus network · built in EVE-NG", 16, "#888780")

    def rect(self, x, y, w, h, fill, stroke, rx=0, sw=2, dash=None, opacity=None):
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"'
        s += f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        s += f' stroke-dasharray="{dash}"' if dash else ""
        s += f' opacity="{opacity}"' if opacity else ""
        self.el.append(s + "/>")

    def text(self, x, y, s, size=18, color=MUTED, anchor="start", weight=400, mono=False):
        fam = MONO if mono else SANS
        self.el.append(
            f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}" font-weight="{weight}" xml:space="preserve">{html.escape(s)}</text>'
        )

    def box(self, x, y, w, h, title, sub=None, style="net", rx=12, tsize=26, ssize=17):
        fill, stroke, tc, sc = STYLES[style]
        self.rect(x, y, w, h, fill, stroke, rx)
        cx = x + w / 2
        if sub:
            self.text(cx, y + h / 2 - 4, title, tsize, tc, "middle", 700)
            self.text(cx, y + h / 2 + 24, sub, ssize, sc, "middle")
        else:
            self.text(cx, y + h / 2 + tsize * 0.35, title, tsize, tc, "middle", 700)

    def path(self, pts, color=LINE, width=2.5, dash=None, arrow=False):
        d = "M" + " L".join(f"{x} {y}" for x, y in pts)
        s = f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"'
        s += f' stroke-dasharray="{dash}"' if dash else ""
        if arrow:
            mid = "m" + color.strip("#")
            self.markers.add((mid, color))
            s += f' marker-end="url(#{mid})"'
        self.el.append(s + "/>")

    def chip(self, x, y, label, style="note", size=18, pad=16):
        fill, stroke, tc, _ = STYLES[style]
        w = int(len(label) * size * 0.68) + pad * 2
        self.rect(x, y, w, size + 20, fill, stroke, (size + 20) / 2, 1.5)
        self.text(x + w / 2, y + size + 5, label, size, tc, "middle", 700)
        return w

    def code(self, x, y, w, lines, size=19):
        h = len(lines) * (size + 11) + 30
        self.rect(x, y, w, h, "#2C2C2A", None, 10)
        for i, ln in enumerate(lines):
            self.text(x + 22, y + 38 + i * (size + 11), ln, size, "#F1EFE8", mono=True)
        return h

    def save(self, path):
        defs = "".join(
            f'<marker id="{mid}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M1 1L9 5L1 9z" fill="{c}"/></marker>'
            for mid, c in sorted(self.markers)
        )
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">'
            f"<title>{html.escape(self.title or 'Lab 1')}</title><desc>{html.escape(self.desc)}</desc>"
            f"<defs>{defs}</defs>" + "".join(self.el) + "</svg>"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)


def topology_elements(d, ox=0, oy=0, labels=True):
    """Draw the tree topology. ox/oy shift it; labels toggles port text."""
    def X(v): return v + ox
    def Y(v): return v + oy
    d.box(X(660), Y(160), 280, 64, "Internet (Cloud0)", style="ext", tsize=22)
    d.box(X(660), Y(280), 280, 84, "R1", "Edge router · NAT", "net")
    d.box(X(620), Y(450), 360, 84, "CORE", "Layer 3 switch · VLAN gateways", "net")
    d.box(X(260), Y(600), 300, 84, "ACC1", "Access switch", "net")
    d.box(X(1040), Y(600), 300, 84, "ACC2", "Access switch", "net")
    d.box(X(260), Y(750), 300, 84, "PC1", "Windows 10 · 10.10.10.50", "host")
    d.box(X(1040), Y(750), 300, 84, "SRV1", "Ubuntu Server · 10.10.20.10", "host")
    d.path([(X(800), Y(224)), (X(800), Y(280))])
    d.path([(X(800), Y(364)), (X(800), Y(450))])
    d.path([(X(720), Y(534)), (X(720), Y(567)), (X(410), Y(567)), (X(410), Y(600))], width=4)
    d.path([(X(880), Y(534)), (X(880), Y(567)), (X(1190), Y(567)), (X(1190), Y(600))], width=4)
    d.path([(X(410), Y(684)), (X(410), Y(750))])
    d.path([(X(1190), Y(684)), (X(1190), Y(750))])
    if labels:
        d.text(X(816), Y(260), "e0/0 · DHCP from home router", 17)
        d.text(X(816), Y(388), "e0/1 · 10.10.0.1", 17)
        d.text(X(816), Y(414), "10.10.0.0/30 · OSPF area 0", 17, "#534AB7", weight=700)
        d.text(X(816), Y(440), "e0/0 · 10.10.0.2", 17)
        d.text(X(704), Y(556), "e0/1", 17, anchor="end")
        d.text(X(565), Y(556), "802.1Q trunk", 17, "#534AB7", "middle", 700)
        d.text(X(426), Y(590), "e0/0", 17)
        d.text(X(896), Y(556), "e0/2", 17)
        d.text(X(1035), Y(556), "802.1Q trunk", 17, "#534AB7", "middle", 700)
        d.text(X(1206), Y(590), "e0/0", 17)
        d.text(X(426), Y(724), "e0/1 · access VLAN 10", 17)
        d.text(X(1206), Y(724), "e0/1 · access VLAN 20", 17)


def d_topology(out):
    d = Diagram("Lab 1 topology", "Campus network with VLANs, trunks, inter-VLAN routing, OSPF and NAT",
                "Internet connects to router R1, then to layer 3 switch CORE, which trunks to access switches ACC1 and ACC2. PC1 is in VLAN 10 on ACC1 and SRV1 is in VLAN 20 on ACC2.")
    topology_elements(d)
    d.rect(1090, 170, 450, 196, "#FFFFFF", "#B4B2A9", 12, 1.5)
    d.text(1114, 206, "VLANs (gateways on CORE)", 19, INK, weight=700)
    rows = [("10", "USERS", "10.10.10.0/24"), ("20", "SERVERS", "10.10.20.0/24"), ("99", "MGMT", "10.10.99.0/24")]
    for i, (v, n, s) in enumerate(rows):
        y = 246 + i * 36
        d.text(1114, y, f"VLAN {v}", 18, INK, mono=True)
        d.text(1214, y, n, 18, MUTED, mono=True)
        d.text(1330, y, s, 18, MUTED, mono=True)
    d.rect(60, 170, 330, 150, "#FFFFFF", "#B4B2A9", 12, 1.5)
    for i, (st, lab) in enumerate([("net", "Network device"), ("host", "Host"), ("ext", "External network")]):
        f, s, _, _ = STYLES[st]
        d.rect(84, 194 + i * 40, 26, 26, f, s, 6)
        d.text(124, 214 + i * 40, lab, 18, INK)
    d.save(os.path.join(out, "01-topology.svg"))


def d_packet_path(out):
    d = Diagram("How PC1 reaches SRV1", "Inter-VLAN routing: the frame changes VLAN at the layer 3 switch",
                "A packet travels from PC1 through ACC1 over a trunk to CORE, is routed from VLAN 10 to VLAN 20, then travels over a trunk to ACC2 and on to SRV1.")
    d.rect(70, 300, 730, 290, "#FAEEDA", "#BA7517", 16, 1.5, dash="8 6")
    d.rect(800, 300, 730, 290, "#E6F1FB", "#378ADD", 16, 1.5, dash="8 6")
    d.text(96, 340, "VLAN 10 · USERS · 10.10.10.0/24", 20, "#633806", weight=700)
    d.text(1504, 340, "VLAN 20 · SERVERS · 10.10.20.0/24", 20, "#0C447C", "end", 700)
    xs = [100, 400, 690, 980, 1280]
    names = [("PC1", "10.10.10.50", "host"), ("ACC1", "Access switch", "net"), ("CORE", "Routes here", "net"),
             ("ACC2", "Access switch", "net"), ("SRV1", "10.10.20.10", "host")]
    for x, (t, s, st) in zip(xs, names):
        d.box(x, 400, 220, 100, t, s, st)
    hops = ["access port", "trunk, tag 10", "trunk, tag 20", "access port"]
    for i, lab in enumerate(hops):
        x1, x2 = xs[i] + 220, xs[i + 1]
        d.path([(x1 + 6, 450), (x2 - 8, 450)], "#444441", 3, arrow=True)
        d.text((x1 + x2) / 2, 540, lab, 17, INK, "middle")
    d.text(800, 250, "Vlan10 10.10.10.1  →  Vlan20 10.10.20.1", 20, "#26215C", "middle", 700, mono=True)
    d.path([(800, 262), (800, 392)], "#534AB7", 2, dash="5 5", arrow=True)
    steps = [
        "1  PC1 sees that 10.10.20.10 is outside its subnet, so it sends the packet to its gateway, 10.10.10.1.",
        "2  ACC1 puts the frame in VLAN 10 and carries it up the trunk with an 802.1Q tag of 10.",
        "3  CORE receives it on interface Vlan10, looks up 10.10.20.0/24, and sends it out of interface Vlan20.",
        "4  The frame goes down the other trunk tagged 20, and ACC2 delivers it untagged to SRV1.",
    ]
    for i, s in enumerate(steps):
        d.text(100, 660 + i * 44, s, 20, INK)
    d.save(os.path.join(out, "02-inter-vlan-path.svg"))


def d_ospf_nat(out):
    d = Diagram("Reaching the internet", "OSPF shares the routes, NAT hides the private addresses",
                "R1 connects to the home router on its outside interface and to CORE on its inside interface. OSPF exchanges a default route and the VLAN subnets. NAT translates inside addresses to R1's outside address.")
    d.box(120, 180, 340, 84, "Home router", "192.168.1.1 · internet", "ext")
    d.box(120, 420, 340, 100, "R1", "Router ID 1.1.1.1", "net")
    d.box(120, 690, 340, 100, "CORE", "Router ID 2.2.2.2", "net")
    d.path([(290, 264), (290, 420)])
    d.path([(290, 520), (290, 690)])
    d.text(306, 330, "e0/0 · DHCP address", 17)
    d.text(306, 356, "ip nat outside", 17, "#534AB7", weight=700, mono=True)
    d.text(306, 556, "e0/1 · 10.10.0.1/30", 17)
    d.text(306, 582, "ip nat inside", 17, "#534AB7", weight=700, mono=True)
    d.text(306, 670, "e0/0 · 10.10.0.2/30", 17)

    d.rect(700, 180, 840, 290, "#FFFFFF", "#B4B2A9", 14, 1.5)
    d.text(730, 224, "OSPF area 0: what each side tells the other", 22, INK, weight=700)
    d.box(730, 256, 150, 60, "R1", style="net", tsize=22)
    d.path([(890, 286), (990, 286)], "#534AB7", 3, arrow=True)
    d.box(1000, 256, 150, 60, "CORE", style="net", tsize=22)
    d.text(1174, 280, "Default route 0.0.0.0/0", 18, INK, weight=700)
    d.text(1174, 304, "default-information originate", 15, MUTED, mono=True)
    d.box(730, 366, 150, 60, "CORE", style="net", tsize=22)
    d.path([(890, 396), (990, 396)], "#534AB7", 3, arrow=True)
    d.box(1000, 366, 150, 60, "R1", style="net", tsize=22)
    d.text(1174, 380, "10.10.10.0/24 · 10.10.20.0/24", 18, INK, weight=700)
    d.text(1174, 404, "10.10.99.0/24", 18, INK, weight=700)
    d.text(1174, 428, "network ... area 0", 15, MUTED, mono=True)

    d.rect(700, 510, 840, 290, "#FFFFFF", "#B4B2A9", 14, 1.5)
    d.text(730, 554, "NAT overload on R1: one outside address for every host", 22, INK, weight=700)
    d.box(730, 596, 330, 110, "Inside packet", "src 10.10.10.50 → dst 8.8.8.8", "warn", tsize=22, ssize=17)
    d.path([(1070, 651), (1170, 651)], "#444441", 3, arrow=True)
    d.box(1180, 596, 330, 110, "Outside packet", "src 192.168.1.x → dst 8.8.8.8", "good", tsize=22, ssize=17)
    d.text(730, 756, "ip nat inside source list 1 interface e0/0 overload", 18, "#26215C", mono=True)
    d.save(os.path.join(out, "03-ospf-and-nat.svg"))


def _panel(d, x, y, w, h, heading, style):
    fill, stroke, tc, _ = STYLES[style]
    d.rect(x, y, w, h, "#FFFFFF", stroke, 16, 2)
    d.chip(x + 24, y - 20, heading, style, 20)


def d_ts_vlan(out):
    d = Diagram("Troubleshooting: server cannot reach its gateway", "An access port in the wrong VLAN",
                "Before the fix, ACC2 port e0/1 was in VLAN 10 so SRV1 could not reach its gateway in VLAN 20. After moving the port to VLAN 20 the ping succeeds.")
    for i, (px, head, st, acc_sub, acc_style, out_lines, expl) in enumerate([
        (60, "Before", "bad", "e0/1 in VLAN 10", "bad",
         ["root@ubuntu:~# ping -c 3 10.10.20.1", "Destination Host Unreachable", "3 transmitted, 0 received"],
         ["SRV1's ARP request for 10.10.20.1 goes out in", "VLAN 10, where no device owns that address."]),
        (820, "After", "good", "e0/1 in VLAN 20", "good",
         ["root@ubuntu:~# ping -c 3 10.10.20.1", "64 bytes from 10.10.20.1: time=1.08 ms", "3 transmitted, 3 received, 0% loss"],
         ["SRV1 and its gateway are in the same VLAN,", "so ARP is answered and the ping replies."]),
    ]):
        _panel(d, px, 190, 720, 440, head, st)
        d.box(px + 30, 250, 190, 96, "SRV1", "10.10.20.10", "host", tsize=22, ssize=16)
        d.box(px + 265, 250, 190, 96, "ACC2", acc_sub, acc_style, tsize=22, ssize=16)
        d.box(px + 500, 250, 190, 96, "CORE", "Vlan20 10.10.20.1", "net", tsize=22, ssize=16)
        d.path([(px + 220, 298), (px + 265, 298)])
        d.path([(px + 455, 298), (px + 500, 298)], width=4)
        d.code(px + 30, 376, 660, out_lines, 18)
        for j, e in enumerate(expl):
            d.text(px + 30, 540 + j * 28, e, 19, INK)
    d.text(60, 690, "How it was found", 22, INK, weight=700)
    d.text(60, 724, "show vlan brief on ACC2 listed Et0/1 under", 19, INK)
    d.text(60, 752, "10 USERS, with no ports in 20 SERVERS.", 19, INK)
    d.text(60, 796, "ACC2 had been given ACC1's access-port config.", 19, MUTED)
    d.code(820, 668, 720, ["ACC2(config)# interface e0/1", "ACC2(config-if)# switchport mode access",
                           "ACC2(config-if)# switchport access vlan 20"], 19)
    d.save(os.path.join(out, "04-troubleshooting-wrong-vlan.svg"))


def d_ts_ospf(out):
    d = Diagram("Troubleshooting: no default route on CORE", "OSPF neighbours need matching subnet masks",
                "Before the fix, R1 used a /30 mask and CORE used a /24 mask on the same link, so OSPF formed no adjacency. After correcting CORE to /30, CORE learned the default route.")
    for px, head, st, core_sub, core_style, out_lines, expl in [
        (60, "Before", "bad", "e0/0 10.10.0.2 /24", "bad",
         ["CORE# show ip route", "Gateway of last resort is not set",
          "C  10.10.0.0/24 is directly connected, Et0/0"],
         ["The hello packets carry each side's mask. They", "differ, so the routers never become neighbours."]),
        (820, "After", "good", "e0/0 10.10.0.2 /30", "good",
         ["CORE# show ip route", "Gateway of last resort is 10.10.0.1",
          "O*E2 0.0.0.0/0 [110/1] via 10.10.0.1"],
         ["Masks match, the adjacency forms, and CORE", "learns the default route that R1 advertises."]),
    ]:
        _panel(d, px, 190, 720, 440, head, st)
        d.box(px + 50, 250, 270, 96, "R1", "e0/1 10.10.0.1 /30", "net", tsize=22, ssize=16)
        d.box(px + 400, 250, 270, 96, "CORE", core_sub, core_style, tsize=22, ssize=16)
        d.path([(px + 320, 298), (px + 400, 298)])
        d.code(px + 30, 376, 660, out_lines, 18)
        for j, e in enumerate(expl):
            d.text(px + 30, 540 + j * 28, e, 19, INK)
    d.text(60, 690, "How it was found", 22, INK, weight=700)
    d.text(60, 724, "CORE's routing table showed the R1 link as", 19, INK)
    d.text(60, 752, "10.10.0.0/24, where the design called for /30.", 19, INK)
    d.code(820, 668, 720, ["CORE(config)# interface e0/0",
                           "CORE(config-if)# ip address 10.10.0.2 255.255.255.252"], 19)
    d.save(os.path.join(out, "05-troubleshooting-ospf-mask.svg"))


def d_cover(out):
    d = Diagram(None, None, "Cover image: campus network lab built in EVE-NG, with a small topology diagram.")
    d.title = "Campus network lab in EVE-NG"
    d.text(80, 250, "Campus network lab", 72, INK, weight=700)
    d.text(80, 330, "Built from scratch in EVE-NG", 40, "#534AB7", weight=700)
    d.text(80, 410, "Six devices, three VLANs, one routed core,", 26, MUTED)
    d.text(80, 448, "and a path to the internet.", 26, MUTED)
    x = 80
    for lab in ["VLANs", "802.1Q trunks", "Inter-VLAN routing"]:
        x += d.chip(x, 520, lab, "net", 20) + 14
    x = 80
    for lab in ["OSPF", "NAT", "Troubleshooting"]:
        x += d.chip(x, 580, lab, "host", 20) + 14
    d.text(80, 800, "Lab 1 · Homelab series", 22, "#888780")
    ox, oy = 880, 90
    d.box(ox + 220, oy + 40, 200, 60, "Internet", style="ext", tsize=22)
    d.box(ox + 220, oy + 170, 200, 70, "R1", style="net")
    d.box(ox + 190, oy + 320, 260, 70, "CORE", style="net")
    d.box(ox + 20, oy + 480, 220, 70, "ACC1", style="net")
    d.box(ox + 400, oy + 480, 220, 70, "ACC2", style="net")
    d.box(ox + 20, oy + 630, 220, 70, "PC1", style="host")
    d.box(ox + 400, oy + 630, 220, 70, "SRV1", style="host")
    d.path([(ox + 320, oy + 100), (ox + 320, oy + 170)])
    d.path([(ox + 320, oy + 240), (ox + 320, oy + 320)])
    d.path([(ox + 260, oy + 390), (ox + 260, oy + 435), (ox + 130, oy + 435), (ox + 130, oy + 480)], width=4)
    d.path([(ox + 380, oy + 390), (ox + 380, oy + 435), (ox + 510, oy + 435), (ox + 510, oy + 480)], width=4)
    d.path([(ox + 130, oy + 550), (ox + 130, oy + 630)])
    d.path([(ox + 510, oy + 550), (ox + 510, oy + 630)])
    d.save(os.path.join(out, "00-cover.svg"))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out, exist_ok=True)
    for fn in (d_cover, d_topology, d_packet_path, d_ospf_nat, d_ts_vlan, d_ts_ospf):
        fn(out)
    print("wrote diagrams to", out)
