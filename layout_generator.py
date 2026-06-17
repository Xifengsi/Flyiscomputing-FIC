#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flyiscomputing (FIC v1.0) - Core Hardware Layout Generator
Originally conceived and invented by Xifeng Si (思希峰).

This script uses gdsfactory to generate the GDSII layout mask for:
1. Spatial Dual-Track Differential Push-Pull Input Ports (Track A & Track B).
2. Non-Von Neumann Co-Flying Spiral Delay Lines for In-Flight Storage.
"""

import numpy as np
import gdsfactory as gf
from gdsfactory.generic_tech import LAYER

@gf.cell
def make_differential_input_ports(
    waveguide_width: float = 0.5,
    track_spacing: float = 4.0,
    port_length: float = 100.0,
    layer_waveguide=LAYER.WG,
    layer_electrode=LAYER.M1
) -> gf.Component:
    """
    Generates the Spatial Dual-Track Differential Topology (Track A & Track B).
    Implements the core push-pull phase modulation foundation with rigorous 
    geometric symmetry to ensure massive Common-Mode Rejection Ratio (CMRR).
    """
    c = gf.Component("FIC_Differential_Input_Ports")
    
    # Calculate Y-positions for perfectly symmetrical parallel tracks
    y_track_a = track_spacing / 2.0
    y_track_b = -track_spacing / 2.0

    # 1. Draw Optical Track A (Push)
    track_a = c << gf.components.straight(
        length=port_length, 
        width=waveguide_width, 
        layer=layer_waveguide
    )
    track_a.movey(y_track_a)

    # 2. Draw Optical Track B (Pull)
    track_b = c << gf.components.straight(
        length=port_length, 
        width=waveguide_width, 
        layer=layer_waveguide
    )
    track_b.movey(y_track_b)

    # 3. Draw Symmetrical Push-Pull Electrodes Placeholder (Thin-Film Lithium Niobate Interface)
    electrode_width = 15.0
    electrode_gap = 2.0
    
    # Center Ground Electrode (shared between Track A and Track B for differential push-pull)
    g_electrode = c << gf.components.straight(
        length=port_length * 0.8,
        width=track_spacing - waveguide_width - (electrode_gap * 2),
        layer=layer_electrode
    )
    g_electrode.movex(port_length * 0.1)

    # Signal Electrode A (Push)
    s_electrode_a = c << gf.components.straight(
        length=port_length * 0.8,
        width=electrode_width,
        layer=layer_electrode
    )
    s_electrode_a.move((port_length * 0.1, y_track_a + (waveguide_width/2) + electrode_gap + (electrode_width/2)))

    # Signal Electrode B (Pull)
    s_electrode_b = c << gf.components.straight(
        length=port_length * 0.8,
        width=electrode_width,
        layer=layer_electrode
    )
    s_electrode_b.move((port_length * 0.1, y_track_b - (waveguide_width/2) - electrode_gap - (electrode_width/2)))

    # Add standard optical and electrical ports for automated routing
    c.add_port("o_in_A", port=track_a.ports["o1"])
    c.add_port("o_out_A", port=track_a.ports["o2"])
    c.add_port("o_in_B", port=track_b.ports["o1"])
    c.add_port("o_out_B", port=track_b.ports["o2"])

    return c

@gf.cell
def make_coflying_spiral_delay(
    target_delay_ps: float = 50.0,
    waveguide_width: float = 0.5,
    min_bend_radius: float = 10.0,
    spacing: float = 2.0,
    layer_waveguide=LAYER.WG
) -> gf.Component:
    """
    Generates a low-loss Si3N4 Spiral Delay Line for Instantaneous Co-Flying Storage.
    Converts advanced temporal Batch queuing into rigid, passive physical spatial paths.
    
    Formula: Length = (Delay * c_vacuum) / group_index
    For Si3N4 at 1550nm, group_index is approximately 2.0.
    """
    c = gf.Component(f"FIC_Spiral_Delay_{target_delay_ps}ps")
    
    # Physical Constants
    c_vacuum = 299792458 * 1e6  # um/s
    group_index = 2.0           # Effective group index for Si3N4 strip waveguide
    
    # Calculate required physical length in micrometers
    required_length_um = (target_delay_ps * 1e-12) * c_vacuum / group_index
    print(f"[FIC Compiler Inference] Target Delay: {target_delay_ps} ps -> Required Waveguide Length: {required_length_um:.2f} um")

    # Generate an Archimedean spiral to meet the exact delay requirements within a compact footprint
    # Using gdsfactory built-in spiral generator for low-loss adiabatic bends
    num_loops = int(np.ceil(np.sqrt(required_length_um * spacing / (4 * np.pi**2 * min_bend_radius**3))))
    num_loops = max(2, num_loops) # Ensure at least 2 loops

    spiral = c << gf.components.spiral_inner_io(
        gap=spacing,
        length=required_length_um,
        width=waveguide_width,
        radius=min_bend_radius,
        layer=layer_waveguide
    )
    
    c.add_port("o_in", port=spiral.ports["o1"])
    c.add_port("o_out", port=spiral.ports["o2"])
    return c

if __name__ == "__main__":
    print("=========================================================================")
    print("  Flyiscomputing (FIC v1.0) - GDSII Hardware Mask Generator")
    print("  Invented and Proposed by Xifeng Si (思希峰)")
    print("=========================================================================\n")

    # 1. Initialize Global IC Component
    fic_chip = gf.Component("FIC_v1_0_Top_Level_Mask")

    # 2. Instantiate pushing-pulling ports
    print("[Structuring] Generating Spatial Dual-Track Differential Push-Pull Input Subsystem...")
    diff_ports = fic_chip << make_differential_input_ports(port_length=150.0, track_spacing=5.0)
    
    # 3. Instantiate a 50ps Co-Flying Storage Unit (Spiral Delay Line)
    print("[Structuring] Generating 50ps Si3N4 Co-Flying Spiral Delay Line Module...")
    spiral_storage = fic_chip << make_coflying_spiral_delay(target_delay_ps=50.0, min_bend_radius=15.0)
    
    # 4. Rigorously route Track A output directly to the In-Flight Storage Module
    spiral_storage.connect("o_in", diff_ports.ports["o_out_A"])

    # 5. Export GDSII files for standard Foundry stream-in (e.g., TSMC, SMIC, AimPhotonics)
    gds_filename = "FIC_v1_0_Hardware_Core.gds"
    fic_chip.write_gds(gds_filename)
    
    print(f"\n[Success] GDSII Layout Compilation Complete!")
    print(f"[Output Target] File saved as -> '{gds_filename}'")
    print("You can now open this file in KLayout to inspect the physical masks of Xifeng Si's architecture.")
    print("=========================================================================")
