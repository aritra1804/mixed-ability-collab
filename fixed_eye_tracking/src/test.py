import tkinter as tk
import time

def show_target(canvas, x, y, size=20, duration=5):
    """
    Clears the canvas, draws a red target circle at (x, y), then holds it for the specified duration.
    The entire circle (of diameter 2*size) will be drawn.
    """
    canvas.delete("all")
    # Draw a circle with center (x, y)
    canvas.create_oval(x - size, y - size, x + size, y + size, fill="red", outline="")
    canvas.update()
    time.sleep(duration)

def run_targets():
    # Create an initial full-screen window to display instructions
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.configure(background="black")
    canvas = tk.Canvas(root, bg="black")
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Force update to get correct screen dimensions later
    root.update()
    
    instructions = tk.Label(root,
                            text="Fixate on the red dot.\nPress any key to start the target sequence.",
                            fg="white", bg="black", font=("Helvetica", 24))
    instructions.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    # Wait for any key press to start the sequence
    root.bind("<Key>", lambda event: root.quit())
    root.mainloop()
    root.destroy()
    
    # Create a new full-screen window for the target sequence
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.configure(background="black")
    canvas = tk.Canvas(root, bg="black")
    canvas.pack(fill=tk.BOTH, expand=True)
    root.update()  # Update to ensure correct dimensions
    
    # Get the full-screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Set the target size and margin
    target_size = 20
    margin = target_size  # Using target_size as margin ensures the circle is fully visible
    
    # Compute target positions ensuring full circles are visible:
    # For the top targets, use margin as y; for bottom targets, use screen_height - target_size
    targets = [
        (margin, margin),                              # Top-left
        (screen_width - margin, margin),               # Top-right
        (margin, screen_height - target_size),         # Bottom-left
        (screen_width - margin, screen_height - target_size),  # Bottom-right
        (screen_width // 2, screen_height // 2)         # Center
    ]
    
    # Show each target for 5 seconds
    for (x, y) in targets:
        show_target(canvas, x, y, size=target_size, duration=5)
    
    # Display completion message
    canvas.delete("all")
    canvas.create_text(screen_width // 2, screen_height // 2,
                       text="Target sequence complete",
                       fill="white", font=("Helvetica", 36))
    canvas.update()
    time.sleep(3)
    
    root.destroy()

if __name__ == "__main__":
    run_targets()
