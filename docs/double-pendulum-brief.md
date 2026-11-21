# ChaosSwing: double pendulum design brief (2026-11-21)

Question: how to design a 3D-printable desk double pendulum that stays chaotic >= 20-30 s (ideally 60 s+) after a big release.

Method note: web search + page fetches. Several maker pages (Instructables, MakerWorld, Printables) returned 403 or title-only to the fetcher, so prior-art facts come from search-result summaries of those pages. Treat them as "listing says", not as read in full. [ENG] = my engineering judgement/calculation, not sourced.

## Answer / recommendation
- Use 608 bearings (8x22x7 mm), TWO per joint, open or shielded (ZZ), with seal/grease reduced. Every printed double pendulum found uses 608s, so parts and CAD precedent are plentiful. Support-skeleton "wobble" is the main killer, so stiffness of the stand matters more than the bearing grade.
- Equal arms (~200 mm pivot-to-pivot), roughly equal masses, with steel weights concentrated at the arm ends [ENG]. Weights raise stored energy relative to bearing friction.
- Fixed M8 bolt axles (stationary inner race, clamped by nut), arms rotate on the outer races. Bearing friction is NOT the limit at this size, rather mount vibration, bearing-seat slop and air drag [ENG estimate below].
- Heavy rigid base (>= 1 kg, or clamp), stand offset so both arms rotate fully in a plane in front of the upright.
- Print in PLA (stiffer than PETG), arms as flat I/box-section with walls along the length.
- LED + CR2032 on the tip for long-exposure photos; angle-marked release jig for repeatable starts.
- Run time expectation: chaos for 30-60 s plausible [ENG, not measured]; prototype and measure before promising 60 s+.

## 1. Prior art
| Design | Bearings / hardware | Notes | Source |
|---|---|---|---|
| MakerWorld "Chaos Pendulum" 999326 | 608 | Listing: 608 for smooth motion; extra bearings used as counterweights | https://makerworld.com/models/999326 |
| MakerWorld "Ring & Bar Double Pendulum" 135793 | 2x 608 (+4 optional as weights) | Maker suggests thrift-store roller-blade 608s (16 per pair) as cheap source; mount via clamp/double-sided tape | https://makerworld.com/models/135793 |
| Thingiverse "Double Pendulum [clamp to desk]" | 2x 608 (+1 optional counterweight), clamp, hot glue | Author warns bearing-to-part clearance is 0.2 mm; may need tuning | https://stlfinder.com/model/double-pendulum-clamp-to-desk-rE61xp6A/2046781 |
| Printables 89444 Chaos pendulum toy | 6x 608 (4 for the double), M3 screws+nuts; also triple | Reconfigurable | https://www.printables.com/model/89444-chaos-pendulum-toy |
| Printables 233054 / 88125 / 147320 fidget double pendulums | 3x 608, M3 fasteners | Handheld, not a desk chaos display | https://www.printables.com/model/233054-double-pendulum-fidget-toy |
| Instructables Double Pendulum Fidget Spinner | 608 too big for arm 2; smaller bearings (695ZZ variant) | Shows size/weight trade-off | https://www.instructables.com/Double-Pendulum-Fidget-Spinner |
| Harvard Natural Sciences demo | 5/8" ball bearings at pivots | Warns mount vibrations steal energy, shortening swing | https://sciencedemonstrations.fas.harvard.edu/presentations/chaotic-pendulum |
| Instructables "Chaos Machine" | Says sleeve bushings would likely work as well as ball bearings; bottom arm can be locked (turns it into a non-chaotic physical pendulum) | | https://www.instructables.com/The-Chaos-Machine-Double-Pendulum |
| Instructables long-exposure builds | Acrylic/balsa/cardboard arms; LED + CR2032 or 9 V; 30 s exposures typical; snug bearing fit with a drop of glue; "more weight at arm ends needs more counterweights" | | https://www.instructables.com/Electric-Double-Pendulum , https://www.instructables.com/Light-Harmonogram , https://www.instructables.com/Long-Exposure-Light-Sculpture |
| Cornell lab manual | Low-angle release gives simple periodic motion; critical angle ~100 deg for their device; friction drives chaotic-to-periodic transition | | https://www.chess.cornell.edu/sites/default/files/inline-files/ll-dp-manual.pdf |

NOT VERIFIED: measured run times of any of these builds; no source found giving seconds of chaos. Commercial desk toys not researched (no result produced specs).

## 2. Bearings and axles
- 608 = 8 mm bore, 22 mm OD, 7 mm wide: https://www.mcmaster.com/products/bearings/bearing-trade-number~608/ (via search summary). Deep-groove friction coefficient 0.0010-0.0015 (normal operation): https://www.jtekt.co.jp/products/bearing/en/support/bearing-knowledge/8-4000.html . Plain bearings 0.01-0.02, i.e. ~10x worse (same page).
- Open bearings shed heat/less drag; 2Z shields vs 2RS contact seals: seals add friction (McMaster listing and SkatePro guide summaries): https://www.mcmaster.com/bearings/bearing-trade-number~608-2z , https://skatepro.com/a19.htm . Recommendation [ENG]: buy 608ZZ (metal shield, non-contact), flush grease with isopropanol/solvent, re-lube with a drop of light oil. NOT VERIFIED: friction torque numbers for degreased 608s; none found.
- Two bearings per joint [ENG]: ~10-20 mm spacing resists tilt/wobble of the printed hub; one bearing per joint (as in most printables) lets the arm rock on its axle. Skip preload (adds friction); clamp inner races with a nut + spacer only snug.
- Axle [ENG]: M8 bolt (8 mm fits bore; use a plain-shank / partially threaded bolt or shoulder bolt so the bearing seats on shank, not threads). M8x50 or similar, steel nut + washers as inner-race spacers.
- FDM seat: printed holes come out ~0.1-0.2 mm small; specify ~0.2 mm larger in XY: https://www.sovol3d.com/blogs/news/3d-printing-bearing-housings-how-to-design-and-fit-bearings-in-fdm-parts (search summary); "0 mm tolerance often too tight on FDM": https://wiki.cci.arts.ac.uk/books/digital-fabrication-lab/page/design-the-clearance-and-tolerance . A PETG study stepped seat diameters in 0.1 mm increments: https://scidar.kg.ac.rs/bitstream/123456789/22638/1/M24-JovanovicPesic-Tribology%20in%20industry.pdf . No source validates a specific 608 number, so: [ENG] print a test coupon with seat dia 21.9 / 22.0 / 22.1 / 22.2 / 22.3 mm, pick the tightest that presses in by hand/vise (press fit, not loose); a tight seat is what keeps the pendulum from rocking. Hot glue or a drop of CA is an accepted fallback (Instructables / Thingiverse above). Print the hub with axis vertical (bore in XY) for roundness [ENG].

## 3. Physics
- Wikipedia analysis assumes identical limbs (length l, mass m); point-mass versions behave similarly. Flip is energetically impossible when 3cos(theta1)+cos(theta2) > 2, so large releases (well above ~90 deg on the upper arm) are needed: https://en.wikipedia.org/wiki/Double_pendulum . Cornell: low-angle release is periodic, critical ~100 deg for their rig (link above).
- Georgia Tech used attachable lead weights to vary parameters and measured time-to-flip: https://nldlab.gatech.edu/w/images/e/e8/Clark-doublependulum.pdf (PDF text unreadable by fetcher; NOT VERIFIED which ratios they recommend). No source found recommending an optimal length/mass ratio.
- Recommendation [ENG]: l1 = l2 (equal), m2 ~ 0.7-1.0 x m1 including tip weights. Equal lengths give the classic wide-ranging motion; a much lighter lower arm decouples less strongly and often settles. Mass concentrated at the ends (weights) gives larger moment of inertia/energy for the same bearing drag, i.e. friction decays energy more slowly in relative terms (Instructables light-sculpture note above says end weights need counterweights, so balance the axle).
- Damping estimate [ENG, order of magnitude only]: bearing torque ~ mu * F * (d/2), mu 0.0015, d = 8 mm. For ~0.4 kg total on joint 1 (F ~4 N): ~2e-5 N m ideal; real greased/skate bearings maybe 10x worse ~2e-4 N m. Release energy for 200 mm arms and ~0.3 kg effective mass ~0.5-1 J. At omega ~ 6-10 rad/s, friction power ~ 2e-4 x 8 x 2 joints ~ 3 mW, so bearing loss alone would take > 100 s to dissipate; air drag, hub rocking and stand vibration (Harvard warning) will dominate and are the likely limit. Target: dense compact arms (low drag area), rigid stand.
- Desk size [ENG]: upper arm 150-250 mm; total reach 2l = 400 mm needs ~420 mm clear radius (~850 mm swept width). 200 mm is a good compromise: pendulum period ~0.9 s, visible, fits 220 mm bed (arm print length ~ 200 + 22 hub = ~225 mm; see part 6).

## 4. Frame / stand [all ENG unless cited]
- Mount vibration steals energy (Harvard link). A printed cantilever upright will flex at the swing frequency; use a short, wide, ribbed upright (>= 30x30 mm section, <= 120 mm free height) or a metal-rod/plate backing.
- Base: >= 1 kg (steel plate or printed shell filled with steel shot/sand/washers) with 200x250 mm footprint and rubber feet; or provide a desk clamp (Thingiverse design above uses a clamp). Pivot axis ~ 120 mm off the base front edge so the system's centre of mass stays over the footprint at full swing.
- Clearance: put the upper axle on a cantilever projecting >= 35 mm from the upright face. Arm 1 in plane A, arm 2 in plane B (offset ~8-10 mm), upright outside both, so both arms can rotate 360 deg without hitting the stand. Use the lower arm tip LED pointing outward (toward the camera).

## 5. Visualising chaos
- LED + CR2032 holder on each tip (Instructables UV/CR2032 and RGB builds above); two colours (e.g. red tip, blue/white mid joint) to separate arms; dark room, camera manual mode, ~30 s exposure (same sources). Maths+ article calls the LED photo a striking illustration: https://plus.maths.org/content/double-trouble .
- Repeatable start [ENG]: printed 180-degree protractor ring around joint 1 with a pin/latch, and a stop lug for arm 2, so two runs from "identical" angles (e.g. 120 deg / 120 deg) differ only by a nudge: shows divergence. Optional second set of marks +-1 deg.
- Weight note [ENG]: LED+holder ~3-4 g; count it in the tip mass.

## 6. Print guidance [ENG unless cited]
- PLA vs PETG: PLA is stiffer: flexural modulus ~4.0 GPa vs 2.1 GPa (makeitfrom), PETG ~1.9 GPa (Ultimaker ISO 178): https://www.makeitfrom.com/compare/Glycol-Modified-Polyethylene-Terephthalate-PETG-PET-G/Polylactic-Acid-PLA-Polylactide , https://um-support-files.ultimaker.com/materials/2.85mm/tds/PETG/Ultimaker-PETG-TDS-v1.00.pdf . PLA is fine indoors (creep/heat are not issues on a desk); use PETG only for bearing hub if tight fit cracking is seen.
- Arms: print flat on the bed, 0.2 mm layers, 0.4 nozzle, 4 perimeters (1.6 mm walls), 25-30% gyroid/grid infill, 5 top/bottom layers; section 20 mm tall (in-plane width 16-20 mm in swing plane stiff direction) x 8 mm thick with lightening holes. Out-of-plane stiffness is what keeps arm 2 from twisting; use a boxed or T cross-section. Orient so layer lines run along the arm.
- Bed 220x220: arm pivot-to-pivot 200 mm + hub radius 11+wall ~ 14 mm each end = ~228 mm, so print diagonally (220x220 diagonal ~310 mm) or use pivot distance 180 mm. Base split into two bolted halves. Check against the actual printer before finalising.

## 7. Baseline design [ENG]
- Arm 1: 200 mm pivot-to-pivot, 8 mm x 20 mm cross-section, ~25-35 g PLA (hub 30 mm dia pocket for 2x 608, 10 mm spacing).
- Arm 2: 200 mm, same section but lighter, ~20-25 g; tip weight pocket + LED holder.
- Axle: M8x50 steel bolt per joint, nut + washers; axle 1 fixed in upright cantilever; axle 2 fixed in arm 1 end, arm 2 rotates on outer races.
- Added mass: ~30 g steel (stack of M8/M10 washers or nuts, or spare 608 bearings as in the MakerWorld designs) at each arm end; balance so each arm's centre-of-mass is near the end, not the hub.
- Base: >= 1 kg, ~200 x 250 mm, 15 mm thick printed shell with steel-washer fill, rubber feet; optional clamp.
- Release jig: 180-deg angle ring, pin lock.
- Tip: LED + CR2032 holder.

BOM (rough; prices NOT VERIFIED except where sourced):
| Item | Qty | Price |
|---|---|---|
| 608ZZ bearings | 4 (+2 spare) | 10-pack 608-2RS about $9.04, 608ZZ 10-pack $12.49 at Walmart (search result 2026-11-21; ABEC-7 8-pack $7.95 at TGM): https://www.walmart.com/ip/Uxcell-608ZZ-Deep-Groove-Ball-Bearings-8x22x7mm-Chrome-Steel-ABEC3-Z3-10-Pack/5050494622 , https://tgmskateboards.com/skateboard-bearings-abec-7-green |
| M8x50 bolts, nuts, washers | 2 sets | ~EUR 2-4 [ENG, unsourced] |
| Steel weights (washers/nuts) | ~60 g | ~EUR 2 [ENG] |
| PLA filament | ~250 g | ~EUR 5 [ENG, ~EUR 20/kg unsourced] |
| Base ballast (steel shot/washers) | ~700 g | ~EUR 5 [ENG] |
| LED + CR2032 + holder | 1-2 | ~EUR 2 [ENG] |
| Total | | roughly EUR 25-35 [ENG] |

## Risks / unknowns
- NOT VERIFIED: any measured chaos duration for any printed build; my 30-60 s figure is an estimate. Plan a quick test: release at 150/150 deg, time to first stop of flips.
- NOT VERIFIED: optimal length/mass ratio and 608 degreased friction values.
- Fit tolerances vary by printer; test coupon needed.
- Prices: only the Walmart/TGM figures were seen in search results; reseller prices change. Prior-art page contents came via search summaries (403 on MakerWorld/Printables).
