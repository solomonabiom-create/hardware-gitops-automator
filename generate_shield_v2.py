import os
import json
import csv
import argparse

def create_advanced_shield(project_name, author_name, rows=2, cols=4):
    if not os.path.exists(project_name):
        os.makedirs(project_name)
    
    pro_path = os.path.join(project_name, f"{project_name}.kicad_pro")
    sch_path = os.path.join(project_name, f"{project_name}.kicad_sch")
    pcb_path = os.path.join(project_name, f"{project_name}.kicad_pcb")
    bom_path = os.path.join(project_name, f"{project_name}_BOM.csv")
    
    pro_data = {
        "meta": { "filename": f"{project_name}.kicad_pro", "version": 1 },
        "project": {
            "back_annotate_modules": True,
            "sheets": [["e8f192b1-0967-4d7a-8fbc-f7b59ef91bd2", "Root"]]
        }
    }
    sch_data = f"(kicad_sch\n  (version 20231120)\n  (uuid \"e8f192b1-0967-4d7a-8fbc-f7b59ef91bd2\")\n  (paper \"A4\")\n  (title_block\n    (title \"{project_name} Advanced Shield\")\n    (company \"{author_name}\")\n  )\n)\n"
    
    geometry_lines = [
        "  (gr_line (start 50 50) (end 118.6 50) (stroke (width 0.15) (type solid)) (layer \"Edge.Cuts\"))",
        "  (gr_line (start 118.6 50) (end 118.6 103.34) (stroke (width 0.15) (type solid)) (layer \"Edge.Cuts\"))",
        "  (gr_line (start 118.6 103.34) (end 50 103.34) (stroke (width 0.15) (type solid)) (layer \"Edge.Cuts\"))",
        "  (gr_line (start 50 103.34) (end 50 50) (stroke (width 0.15) (type solid)) (layer \"Edge.Cuts\"))"
    ]

    def make_header(ref, x_start, y_start, pin_count):
        pads = []
        for p in range(1, pin_count + 1):
            px = x_start + ((p - 1) * 2.54)
            pads.append(f"    (pad \"{p}\" tht circle (at {px - x_start} 0) (size 1.7 1.7) (drill 1.0) (layers \"*.Cu\" \"*.Mask\"))")
        
        joined_pads = '\n'.join(pads)
        return (
            f"  (footprint \"Connector_PinHeader_2.54mm:PinHeader_1x{pin_count:02d}_P2.54mm_Vertical\"\n"
            f"    (layer \"F.Cu\") (at {x_start} {y_start})\n"
            f"    (descr \"Header {ref}\") (path \"/{ref}\")\n"
            f"{joined_pads}\n"
            f"  )"
        )

    footprints = [
        make_header("J_POWER", 62.7,  98.26, 8),
        make_header("J_ANALOG", 85.56, 98.26, 6),
        make_header("J_DIGITAL_L", 52.54, 52.54, 8),
        make_header("J_DIGITAL_H", 74.38, 52.54, 10)
    ]

    matrix_footprints = []
    matrix_traces = []
    bom_items = []
    
    start_x, start_y = 65.0, 65.0
    spacing_x, spacing_y = 12.0, 10.0
    comp_counter = 1
    
    for r in range(rows):
        for c in range(cols):
            r_x = start_x + (c * spacing_x)
            r_y = start_y + (r * spacing_y)
            led_x = r_x
            led_y = r_y + 4.0
            
            r_ref = f"R{comp_counter}"
            led_ref = f"D{comp_counter}"
            
            matrix_footprints.append(
                f"  (footprint \"Resistor_SMD:R_0805_2012Metric_Pad1.15x1.40mm_HandSolder\"\n"
                f"    (layer \"F.Cu\") (at {r_x} {r_y})\n"
                f"    (fp_text reference \"{r_ref}\" (at 0 -1.5) (layer \"F.SilkS\") (effects (font (size 0.8 0.8) (thickness 0.15))))\n"
                f"    (pad \"1\" smd rect (at -1.0 0) (size 1.15 1.4) (layers \"F.Cu\" \"F.Paste\" \"F.Mask\"))\n"
                f"    (pad \"2\" smd rect (at 1.0 0) (size 1.15 1.4) (layers \"F.Cu\" \"F.Paste\" \"F.Mask\"))\n"
                f"  )"
            )
            
            matrix_footprints.append(
                f"  (footprint \"LED_SMD:LED_0805_2012Metric_Pad1.15x1.40mm_HandSolder\"\n"
                f"    (layer \"F.Cu\") (at {led_x} {led_y})\n"
                f"    (fp_text reference \"{led_ref}\" (at 0 1.5) (layer \"F.SilkS\") (effects (font (size 0.8 0.8) (thickness 0.15))))\n"
                f"    (pad \"1\" smd rect (at -1.0 0) (size 1.15 1.4) (layers \"F.Cu\" \"F.Paste\" \"F.Mask\"))\n"
                f"    (pad \"2\" smd rect (at 1.0 0) (size 1.15 1.4) (layers \"F.Cu\" \"F.Paste\" \"F.Mask\"))\n"
                f"  )"
            )
            
            matrix_traces.append(f"  (segment (start {r_x + 1.0} {r_y}) (end {r_x + 1.0} {led_y}) (width 0.3) (layer \"F.Cu\") (net {comp_counter+1}))")
            matrix_traces.append(f"  (segment (start {r_x + 1.0} {led_y}) (end {led_x + 1.0} {led_y}) (width 0.3) (layer \"F.Cu\") (net {comp_counter+1}))")
            
            bom_items.append({"Reference": r_ref, "Value": "220R", "Footprint": "R_0805_2012Metric", "Quantity": 1})
            bom_items.append({"Reference": led_ref, "Value": "Green LED", "Footprint": "LED_0805_2012Metric", "Quantity": 1})
            comp_counter += 1

    bom_items.extend([
        {"Reference": "J_POWER", "Value": "8-Pin Header", "Footprint": "PinHeader_1x08_P2.54mm", "Quantity": 1},
        {"Reference": "J_ANALOG", "Value": "6-Pin Header", "Footprint": "PinHeader_1x06_P2.54mm", "Quantity": 1},
        {"Reference": "J_DIGITAL_L", "Value": "8-Pin Header", "Footprint": "PinHeader_1x08_P2.54mm", "Quantity": 1},
        {"Reference": "J_DIGITAL_H", "Value": "10-Pin Header", "Footprint": "PinHeader_1x10_P2.54mm", "Quantity": 1}
    ])

    zone_lines = [
        "  (zone (net 1) (net_name \"GND\") (layer \"B.Cu\") (tstamp \"zone_gnd\")",
        "    (hatch edge 0.5) (connect_pads (clearance 0.4)) (min_thickness 0.25)",
        "    (polygon (pts (xy 52 52) (xy 116 52) (xy 116 101) (xy 52 101)))",
        "  )"
    ]

    text_lines = [
        f"  (gr_text \"MATRIX SHIELD: {project_name}\" (at 84 56) (layer \"F.SilkS\") (effects (font (size 1.5 1.5) (thickness 0.3) bold) (justify center)))",
        f"  (gr_text \"BOM EXTRACTED VIA PYTHON\" (at 84 92) (layer \"F.SilkS\") (effects (font (size 1.0 1.0) (thickness 0.2)) (justify center)))"
    ]

    # FIX: Pre-compile all text blocks cleanly outside of the f-string allocation block
    str_geometry = '\n'.join(geometry_lines)
    str_footprints = '\n'.join(footprints)
    str_matrix_footprints = '\n'.join(matrix_footprints)
    str_matrix_traces = '\n'.join(matrix_traces)
    str_zone_lines = '\n'.join(zone_lines)
    str_text_lines = '\n'.join(text_lines)

    pcb_data = (
        "(kicad_pcb\n  (version 20240108)\n  (generator \"kicad_pcb_generic\")\n"
        "  (general (thickness 1.6))\n  (paper \"A4\")\n"
        "  (layers\n"
        "    (0 \"F.Cu\" signal) (31 \"B.Cu\" signal)\n"
        "    (36 \"B.SilkS\" user \"B.Silkscreen\") (37 \"F.SilkS\" user \"F.Silkscreen\")\n"
        "    (38 \"B.Mask\" user) (39 \"F.Mask\" user)\n"
        "    (44 \"Edge.Cuts\" user)\n  )\n"
        f"{str_geometry}\n"
        f"{str_footprints}\n"
        f"{str_matrix_footprints}\n"
        f"{str_matrix_traces}\n"
        f"{str_zone_lines}\n"
        f"{str_text_lines}\n"
        ")\n"
    )

    with open(pro_path, "w", encoding="utf-8") as f:
        json.dump(pro_data, f, indent=2)
    with open(sch_path, "w", encoding="utf-8") as f:
        f.write(sch_data)
    with open(pcb_path, "w", encoding="utf-8") as f:
        f.write(pcb_data)

    with open(bom_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Reference", "Value", "Footprint", "Quantity"])
        writer.writeheader()
        writer.writerows(bom_items)

    print(f"\n[✔] Structural files compiled successfully within folder: '{project_name}/'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procedural KiCad 8.0 Array Layout & Manufacturing BOM Script Engine")
    parser.add_argument("-n", "--name", type=str, default="MatrixShield", help="Name of your project output folder")
    parser.add_argument("-a", "--author", type=str, default="Automated Dev", help="Author tag name data metrics string")
    parser.add_argument("-r", "--rows", type=int, default=2, help="Amount of component array layout matrix rows")
    parser.add_argument("-c", "--cols", type=int, default=4, help="Amount of component array layout matrix columns")
    
    args = parser.parse_args()
    create_advanced_shield(args.name, args.author, args.rows, args.cols)
