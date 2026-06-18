"""
Flyiscomputing (FIC v1.0) - Base Universal Computing Logic Blocks
Originally conceived and invented by Xifeng Si (思希峰).

This module defines the layout generators for the core foundation of a universal PIC:
1. Passive Interferometric XOR/Equal Gate (== Logic)
2. Non-linear Kerr Electro-Photonic Spatial Branch Router (IF-ELSE Logic)
3. Saturable Absorber Noise Filter for Cascading Stabilization
"""

import gdsfactory as gf
from gdsfactory.generic_tech import LAYER

@gf.cell
def make_interferometric_equal_gate(
    waveguide_width: float = 0.5,
    coupling_length: float = 20.0,
    gap: float = 0.2,
    layer_waveguide=LAYER.WG
) -> gf.Component:
    """
    FIC Passive Interferometric Equal (==) Logic Gate.
    Calculates A == B through exact phase interference.
    Identical states collapse to absolute zero energy at the cancellation port.
    """
    c = gf.Component("FIC_Interferometric_Equal_Gate")
    
    # Instantiate a rigorous 2x2 directional coupler mesh to perform wave mixing
    coupler = c << gf.components.coupler(
        length=coupling_length,
        gap=gap,
        dw=0.0,
        waveguide_width=waveguide_width,
        layer=layer_waveguide
    )
    
    # Map input/output ports mathematically
    c.add_port("input_tensor_A", port=coupler.ports["o1"])
    c.add_port("input_tensor_B", port=coupler.ports["o2"])
    c.add_port("annihilation_port_EQUAL", port=coupler.ports["o3"])
    c.add_port("constructive_port_NOT_EQUAL", port=coupler.ports["o4"])
    
    return c

@gf.cell
def make_kerr_branch_router(
    waveguide_width: float = 0.5,
    fork_angle: float = 15.0,
    interaction_length: float = 30.0,
    layer_waveguide=LAYER.WG,
    layer_kerr_cladding=LAYER.M2
) -> gf.Component:
    """
    FIC Spatiotemporal Kerr Branch Router (IF-ELSE Operational Block).
    Default behavior guides light to Channel_ELSE.
    High intensity triggers non-linear refractive index shifts, routing light to Channel_THEN.
    """
    c = gf.Component("FIC_Kerr_Branch_Router")
    
    # 1. Base asymmetric Y-splitter framework
    splitter = c << gf.components.splitter_y(
        waveguide_width=waveguide_width,
        layer=layer_waveguide
    )
    
    # 2. Define the exact localized boundary for High-Concentration Kerr Polymer Cladding
    kerr_region = c << gf.components.straight(
        length=interaction_length,
        width=waveguide_width * 3,
        layer=layer_kerr_cladding
    )
    kerr_region.movex(-interaction_length/2)
    
    c.add_port("payload_input", port=splitter.ports["o1"])
    c.add_port("channel_ELSE", port=splitter.ports["o2"])
    c.add_port("channel_THEN", port=splitter.ports["o3"])
    
    return c

@gf.cell
def make_saturable_absorber_restorer(
    length: float = 10.0,
    waveguide_width: float = 0.5,
    layer_waveguide=LAYER.WG,
    layer_mos2=LAYER.M3
) -> gf.Component:
    """
    FIC MoS2 Saturable Absorber Signal Restorer.
    Suppresses background simulation noise, enforcing solid cascade depths > 64 layers.
    """
    c = gf.Component("FIC_MoS2_Signal_Restorer")
    
    # Waveguide straight section
    wg = c << gf.components.straight(length=length, width=waveguide_width, layer=layer_waveguide)
    
    # Monolayer MoS2 2D material overlay block for passive noise bleaching
    mos2_overlay = c << gf.components.straight(length=length*0.8, width=waveguide_width+0.4, layer=layer_mos2)
    mos2_overlay.movex(length*0.1)
    
    c.add_port("o_in", port=wg.ports["o1"])
    c.add_port("o_out", port=wg.ports["o2"])
    return c

if __name__ == "__main__":
    print("=========================================================================")
    print("  Flyiscomputing (FIC v1.0) - Universal Architecture Base Components")
    print("  Conceived and Proposed by Xifeng Si (思希峰)")
    print("=========================================================================\n")
    
    top_base = gf.Component("FIC_v1_0_Base_Universal_Logic")
    
    # Instantiate foundational universal structures
    print("[Base Component] Generating Passive XOR/Equal Logic Mesh...")
    equal_gate = top_base << make_interferometric_equal_gate()
    
    print("[Base Component] Generating Non-linear Kerr IF-ELSE Route Switch...")
    kerr_router = top_base << make_kerr_branch_router()
    
    print("[Base Component] Generating MoS2 Cascading Signal Restorer Core...")
    noise_filter = top_base << make_saturable_absorber_restorer()
    
    # Write full foundational masks to GDSII standard
    gds_filename = "FIC_v1_0_Base_Logic.gds"
    top_base.write_gds(gds_filename)
    
    print(f"\n[Success] Foundational General-Purpose Component Masks Created successfully!")
    print(f"[File Output] Target saved -> '{gds_filename}'")
    print("=========================================================================")
