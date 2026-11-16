# Post series: Lab 1, campus network

Five posts, written for LinkedIn. Each has a matching image in `diagrams/`. Post them a few days apart. Replace `<repo link>` with your repository URL, and edit anything that doesn't sound like you.

---

## Post 1: the kickoff

**Image:** `diagrams/00-cover.png`

I just finished the first lab in my homelab, which I'm building to sharpen my networking and security skills.

Lab 1 is a small campus network, built from an empty canvas in EVE-NG:

→ 3 VLANs for users, servers and management
→ 802.1Q trunks between the access switches and the core
→ Inter-VLAN routing on a layer 3 switch
→ OSPF between the core and the edge router
→ NAT out to the internet

Six devices in total: a router, three switches, a Windows 10 client and an Ubuntu server.

Reading about VLANs and OSPF is one thing. Getting a ping to cross two VLANs, a routed core and a NAT boundary, and understanding every hop it takes, is where it actually sticks.

Over the next few posts I'll share the topology, how the traffic flows, and the mistakes I made along the way. The mistakes taught me the most.

Configs, diagrams and a full build guide are on GitHub: <repo link>

#networking #homelab #EVENG #CCNA #learninginpublic

---

## Post 2: the design

**Image:** `diagrams/01-topology.png`

Here's the design behind my campus network lab.

Three layers, each with one job:

• Access switches (ACC1, ACC2) put each device into a VLAN. PC1 lands in VLAN 10, the server in VLAN 20.
• The core switch (CORE) holds the gateway for every VLAN and routes between them.
• The edge router (R1) connects the campus to the outside and handles NAT.

A few design choices I'd make again:

1. One subnet per VLAN, with the VLAN number in the third octet (VLAN 10 is 10.10.10.0/24, VLAN 20 is 10.10.20.0/24). It makes every address readable at a glance.
2. A /30 on the link between the router and the core. Two devices, two addresses, nothing wasted.
3. A management VLAN created from day one, even though nothing uses it yet.

One thing that surprised me: in EVE-NG the router and the switches use the same Cisco IOL node type. The image you load decides whether the node behaves as a router or a switch.

Repo with the full addressing plan: <repo link>

#networking #networkdesign #VLAN #homelab

---

## Post 3: how a packet crosses VLANs

**Image:** `diagrams/02-inter-vlan-path.png`

Two machines on the same switch infrastructure, in different VLANs. How does one reach the other?

It took building it for this to click, so here's the path from my lab, hop by hop:

1. PC1 (10.10.10.50) wants to reach the server (10.10.20.10). That's a different subnet, so PC1 sends the packet to its default gateway.
2. The access switch tags the frame with VLAN 10 and sends it up the trunk.
3. The core switch receives it on its VLAN 10 interface, checks its routing table, and sends it out of its VLAN 20 interface.
4. The frame travels down the other trunk tagged VLAN 20, and the second access switch delivers it to the server.

The switching is layer 2 all the way, except for one moment at the core where the packet is routed. That single hop is what "inter-VLAN routing" means.

One command makes it possible on the core switch: `ip routing`.

Diagrams and configs: <repo link>

#networking #VLAN #routing #CCNA #homelab

---

## Post 4: the bugs

**Image:** `diagrams/04-troubleshooting-wrong-vlan.png` (add `05-troubleshooting-ospf-mask.png` as a second image)

The most useful part of my campus lab was everything that went wrong.

Fault 1: the server couldn't reach its own gateway.

The ping came back "Destination Host Unreachable" from the server's own address. That means ARP got no reply, which points at layer 2, not routing. `show vlan brief` on the access switch showed the server's port sitting in VLAN 10. It belonged in VLAN 20. I had applied the first switch's config to the second one.

Fault 2: OSPF was configured on both ends and no routes appeared.

The core's routing table showed the link to the router as a /24. The router's side was a /30. OSPF neighbours on the same link must agree on the subnet mask, so they never formed an adjacency. One corrected mask later, the default route showed up.

What I took from it:

• The error message usually tells you which layer to look at.
• Check one hop at a time, starting from the device that's failing.
• When a routing protocol is silent, compare both ends of the link.
• Change one thing, then test.

Full troubleshooting log with the command output: <repo link>

#networking #troubleshooting #OSPF #VLAN #homelab

---

## Post 5: reaching the internet

**Image:** `diagrams/03-ospf-and-nat.png`

Last piece of Lab 1: getting a private campus network onto the internet.

Two things had to work together.

OSPF, so the devices know where things are:
• The core tells the router about the VLAN subnets.
• The router tells the core, "send anything you don't recognise to me."

NAT, so private addresses can leave:
• Every host inside uses a 10.10.x.x address that the internet can't route back to.
• The router rewrites the source address to its own outside address on the way out, and reverses it on the way back.

The final test was three pings from the client: the router, 8.8.8.8, then google.com. Each one proves a different layer: internal routing, NAT, then DNS.

Everything from Lab 1 is here: <repo link>

#networking #OSPF #NAT #homelab #learninginpublic

---

## Short versions

For X, Threads or Bluesky. One image each.

1. Built a campus network from scratch in EVE-NG: 3 VLANs, trunks, a routed core, OSPF and NAT. Six devices, one working path to the internet. Configs and diagrams: <repo link> (image: 00-cover)
2. My campus lab design: access switches place devices in VLANs, the core routes between them, the edge router handles NAT. One job per layer. (image: 01-topology)
3. How a packet crosses VLANs: up a trunk tagged 10, routed once at the core, down another trunk tagged 20. That one routed hop is inter-VLAN routing. (image: 02-inter-vlan-path)
4. "Destination Host Unreachable" from your own IP means ARP failed. Mine was an access port in the wrong VLAN. `show vlan brief` found it in seconds. (image: 04-troubleshooting-wrong-vlan)
5. OSPF configured on both ends, no routes. Cause: a /24 on one side of the link and a /30 on the other. Neighbours must agree on the mask. (image: 05-troubleshooting-ospf-mask)

## Posting tips

- Attach the PNG, not the SVG. The PNGs are 1600×900, which displays well in feeds.
- Put the repository link in the first comment if you find posts with links get less reach.
- Add a screenshot of your own EVE-NG canvas or a console to at least one post. Real screens from your lab are more convincing than diagrams alone.
