import tkinter as tk
from tkinter import messagebox, simpledialog

# XOR utility functions
def xor_encrypt_decrypt(data, key):
    """Encrypt or decrypt data using XOR."""
    return bytes([b ^ key for b in data])

# Save and encrypt the map file
def save_map_to_file(name, level_requirement, special, grid, metadata):
    filename = f"{name}.qscene"

    map_data = {
        "ver": 303,
        "name": name,
        "level_requirement": level_requirement,
        "special": special,
        "tiles": []
    }

    # Add grid and metadata to tiles
    # This is done per tile, since every tile can have a special property
    for y, row in enumerate(grid):
        for x, char in enumerate(row):
            tile_metadata = metadata.get((x, y), {})
            map_data["tiles"].append({
                "x": x,
                "y": y,
                "graphic": tile_metadata.get("graphic", "UNKNOWN"),
                "fluid": tile_metadata.get("fluid", False),
                "dangerous_fluid": tile_metadata.get("dangerous_fluid", 0),
                "npc_spawn": tile_metadata.get("npc_spawn", -1),
                "door": {
                    "locked": tile_metadata.get("door_locked", False),
                    "key_needed": tile_metadata.get("key_needed", "nokey"),
                    "dest_map": tile_metadata.get("dest_map", "nodoorhere"),
                    "dest_coords": tile_metadata.get("dest_coords", {"x": -1, "y": -1})
                },
                "scene_transition": {
                    "is_transition_scene": tile_metadata.get("is_transition_scene", False),
                    "destination_map": tile_metadata.get("destination_map", "nomap"),
                    "destination_coords": tile_metadata.get("destination_coords", {"x": -1, "y": -1})
                },
                "shopkeeper": {
                    "is_shopkeeper": tile_metadata.get("is_shopkeeper", False),
                    "shopkeep_id": tile_metadata.get("shopkeep_id", -1)
                }
            })

    with open(filename, 'w') as f:
        import json
        f.write(json.dumps(map_data, indent=4))

    # Encrypt the file
    key = 0x5A
    with open(filename, 'rb') as f:
        plaintext = f.read()

    ciphertext = xor_encrypt_decrypt(plaintext, key)

    with open(filename, 'wb') as f:
        f.write(ciphertext)

    messagebox.showinfo("Success", f"Map {filename} has been encrypted and saved!")

# GUI logic
def create_map_gui():
    root = tk.Tk()
    root.title("Quartz Map Maker 3.0.3")

    # Metadata frame
    meta_frame = tk.Frame(root)
    meta_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

    tk.Label(meta_frame, text="Map Name:").grid(row=0, column=0, sticky="e")
    name_var = tk.StringVar()
    tk.Entry(meta_frame, textvariable=name_var).grid(row=0, column=1)

    tk.Label(meta_frame, text="Level Requirement:").grid(row=1, column=0, sticky="e")
    level_var = tk.StringVar()
    tk.Entry(meta_frame, textvariable=level_var).grid(row=1, column=1)

    tk.Label(meta_frame, text="Special Map (0/1):").grid(row=2, column=0, sticky="e")
    special_var = tk.StringVar()
    tk.Entry(meta_frame, textvariable=special_var).grid(row=2, column=1)

    # Grid frame
    grid_frame = tk.LabelFrame(root, text="16x16 Grid")
    grid_frame.grid(row=1, column=0, padx=10, pady=10)

    grid_vars = []
    for y in range(16):
        row_vars = []
        for x in range(16):
            var = tk.StringVar()
            entry = tk.Entry(grid_frame, textvariable=var, width=2, justify="center")
            entry.grid(row=y, column=x)
            row_vars.append(var)
        grid_vars.append(row_vars)

    # Metadata frame
    meta_section_frame = tk.Frame(root)
    meta_section_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="n")

    metadata_vars = {
        "graphic": tk.StringVar(),
        "fluid": tk.BooleanVar(),
        "dangerous_fluid": tk.StringVar(),
        "npc_spawn": tk.StringVar(),
        "door_locked": tk.BooleanVar(),
        "key_needed": tk.StringVar(),
        "dest_map": tk.StringVar(),
        "dest_coords_x": tk.StringVar(),
        "dest_coords_y": tk.StringVar(),
        "is_transition_scene": tk.BooleanVar(),
        "destination_map": tk.StringVar(),
        "destination_coords_x": tk.StringVar(),
        "destination_coords_y": tk.StringVar(),
        "is_shopkeeper": tk.BooleanVar(),
        "shopkeep_id": tk.StringVar()
    }

    for i, (key, var) in enumerate(metadata_vars.items()):
        tk.Label(meta_section_frame, text=f"{key.replace('_', '_')}:").grid(row=i, column=0, sticky="e")
        if isinstance(var, tk.BooleanVar):
            tk.Checkbutton(meta_section_frame, variable=var).grid(row=i, column=1, sticky="w")
        else:
            tk.Entry(meta_section_frame, textvariable=var).grid(row=i, column=1)

    active_tile = [0, 0]  # To track the active tile

    def update_active_tile(x, y):
        active_tile[0] = x
        active_tile[1] = y
        tile_metadata = metadata.get((x, y), {})
        for key, var in metadata_vars.items():
            if isinstance(var, tk.BooleanVar):
                var.set(tile_metadata.get(key, False))
            else:
                var.set(tile_metadata.get(key, ""))

    metadata = {}

    for y, row in enumerate(grid_vars):
        for x, cell in enumerate(row):
            cell.trace("w", lambda *args, x=x, y=y: update_active_tile(x, y))

    def save_metadata():
        x, y = active_tile
        metadata[(x, y)] = {
            key: (var.get() if not isinstance(var, tk.BooleanVar) else var.get())
            for key, var in metadata_vars.items()
        }

    def save_map():
        name = name_var.get().strip().upper()
        level_requirement = level_var.get().strip()
        special = special_var.get()

        if not name:
            messagebox.showerror("Error", "Map name is required.")
            return

        grid = [[cell.get() for cell in row] for row in grid_vars]

        save_map_to_file(name, level_requirement, special, grid, metadata)

    tk.Button(meta_section_frame, text="Update Metadata", command=save_metadata).grid(row=len(metadata_vars), column=0, columnspan=2)

    save_button = tk.Button(root, text="Save Map", command=save_map)
    save_button.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_map_gui()
