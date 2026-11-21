# ChaosSwing: SPEC (v1)

Owner request 2026-11-21 (msg 978): "a 3D printable double pendulum that I can see the chaos", public repo, name chosen by agent.
Brief: `research/double-pendulum-brief.md` (2026-11-21). Choices not given by the owner are marked (choice).

## Goal
A desktop double pendulum, printable on a normal FDM printer with cheap standard hardware. After a big release it should swing chaotically for at least 20-30 s, and you should be able to see that two near-identical releases end up very differently.

## Features
1. **Stand:** heavy, stiff base plus an upright and a cantilever arm that carries the main axle.
   - Base has a ballast pocket for >= 1 kg of sand, steel washers or nuts, and 4 holes for screwing or clamping it to a desk or board (choice).
   - Upright is split into <= 2 printed parts joined with bolts and alignment features, since it is taller than the bed.
   - The main axle sits >= 35 mm in front of the upright (brief section 6), so neither arm can touch the upright.
2. **Upper arm:** pivot spacing **160 mm** (choice: fits the 220 bed straight, desk sized).
   - Hub with **2x 608ZZ** bearings, spaced >= 10 mm apart to stop wobble.
   - The elbow end holds an M8 bolt fixed in the arm, which is the lower arm's axle.
3. **Lower arm:** pivot-to-tip **150 mm**, a hub with 2x 608ZZ, and a tip mass mount: an M8 bolt plus a stack of washers or nuts, about 30 g, adjustable.
   - Lower-arm mass is 0.7-1.0x the upper arm (brief section 3), checked from the CAD masses with hardware included.
4. **Separate planes:** stand face, upper arm and lower arm each sit in their own plane with >= 3 mm axial clearance (washers/spacers), so both arms rotate a full 360° with no collision.
5. **Release ring:** a printed 180° (or full) angle scale behind the upper arm, marked every 15°, with pin holes at 90/120/150/180°. A removable pin holds the upper arm at a known angle for repeatable releases (choice).
6. **Visual add-on (optional part):** a tip cap for a 5 mm LED + CR2032 holder on the lower arm tip, for long-exposure chaos photos. Its mass replaces part of the 30 g tip weight.
7. **Bearing test coupon:** a small plate with 608 seats at 21.9 / 22.1 / 22.3 mm, so the owner can pick the press fit for their printer.
8. **Simulation for the README:** a Python double-pendulum simulation using the CAD masses and inertias (rigid bodies, not point masses), with light viscous damping as an assumption.
   - Outputs a GIF/PNG of two releases 0.1° apart diverging, plus the tip trace.
   - Labelled as a simulation, not a measurement.

## Hardware (BOM, bought parts)
- 4x 608ZZ, grease flushed out (brief section 2)
- 2x M8 bolts (main axle 60-70 mm, elbow ~45 mm)
- M8 nuts, nyloc nuts and washers as spacers and tip mass
- M5 or M4 bolts and nuts for the upright splice
- Ballast: about 1 kg of sand, steel washers or nuts
- Optional: 5 mm LED, CR2032 holder and switch

Give each item's quantity and length in a BOM table with rough prices, marked "estimate".

## Print and CAD constraints
- Bed is 220 x 220 x 250 mm, every part must fit. Nozzle 0.4 mm, layers 0.2 mm.
- Material: PLA for the arms (stiffer, brief section 8), PLA or PETG for the stand. Arms print flat with 4 perimeters and 25-30 % infill.
- Tolerances: 608 seat 22.1 mm nominal (coupon to tune). M8 clearance 8.4 mm, M5 5.4 mm. Nut traps +0.2 mm across flats. Sliding fits +0.25 mm.
- Parametric CadQuery source with arm lengths, bearing fit and tip mass as parameters. STEP + STL for every part, assembly STEP, iso.png, exploded view, and the arms at a few poses.
- No supports needed, or at most minimal ones (state which parts need them).

## Acceptance criteria
1. Every printable part fits 220x220x250, and every STL is watertight with valid solids.
2. Collision sweep: the upper arm from 0-360° in 10° steps, and the lower arm from 0-360° relative to it in 10° steps. Zero interference with the stand, the release ring and the other arm (overlap volume about 0).
3. Pivot height above the base top is >= the total reach (160 + 150 + tip radius) + 15 mm. The arms never touch the base or the desk.
4. Mass report from the CAD volumes x density plus hardware: upper and lower arm masses, ratio within 0.7-1.0, CoM and inertia about each pivot.
5. Stability check: with the base and ballast, worst-case swing reactions (hand calculation from the simulated peak pivot force) do not tip the base (state the margin).
6. The simulation runs and writes the divergence plot/GIF. Energy decays monotonically with the damping on, and is conserved within 1 % over 10 s with damping off (sanity test).
7. `tools/run_tests.sh` runs all of the above checks and exits non-zero on any failure.
8. The README covers what it is, a photo/render, the BOM, print settings, the assembly steps (bearing pressing, degreasing, spacer stack, ballast), the release procedure, how to film or photograph the chaos, and the open items. Unverified claims are marked (e.g. run time not measured).

## Delivery
- Public GitHub repo **nsumia/ChaosSwing** (owner approved public in msg 978). MIT license (choice: public maker project).
- Owner gets iso.png, the divergence GIF/PNG and the STL zip via Telegram.
