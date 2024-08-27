import tkinter as tk
from tkinter import filedialog, simpledialog, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import sys
import os

class GifViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("GIF Viewer")
        
        self.label = tk.Label(master)
        self.label.pack()
        
        self.load_button = tk.Button(master, text="Load GIF", command=self.load_gif)
        self.load_button.pack()
        
        self.play_button = tk.Button(master, text="Play/Pause", command=self.toggle_play, state=tk.DISABLED)
        self.play_button.pack()
        
        self.add_text_button = tk.Button(master, text="Add Text", command=self.add_text, state=tk.DISABLED)
        self.add_text_button.pack()
        
        self.save_button = tk.Button(master, text="Save GIF", command=self.save_gif, state=tk.DISABLED)
        self.save_button.pack()
        
        # Font size entry
        self.font_size_frame = tk.Frame(master)
        self.font_size_frame.pack()
        self.font_size_label = tk.Label(self.font_size_frame, text="Font Size:")
        self.font_size_label.pack(side=tk.LEFT)
        self.font_size_entry = tk.Entry(self.font_size_frame, width=5)
        self.font_size_entry.insert(0, "20")  # Default font size
        self.font_size_entry.pack(side=tk.LEFT)
        
        # Text position entries
        self.pos_x_frame = tk.Frame(master)
        self.pos_x_frame.pack()
        self.pos_x_label = tk.Label(self.pos_x_frame, text="X Position (0-1):")
        self.pos_x_label.pack(side=tk.LEFT)
        self.pos_x_entry = tk.Entry(self.pos_x_frame, width=5)
        self.pos_x_entry.insert(0, "0.5")  # Default center position
        self.pos_x_entry.pack(side=tk.LEFT)
        
        self.pos_y_frame = tk.Frame(master)
        self.pos_y_frame.pack()
        self.pos_y_label = tk.Label(self.pos_y_frame, text="Y Position (0-1):")
        self.pos_y_label.pack(side=tk.LEFT)
        self.pos_y_entry = tk.Entry(self.pos_y_frame, width=5)
        self.pos_y_entry.insert(0, "0.9")  # Default bottom position
        self.pos_y_entry.pack(side=tk.LEFT)
        
        # Update button
        self.update_button = tk.Button(master, text="Update Text", command=self.update_text)
        self.update_button.pack()
        
        self.is_playing = False
        self.current_frame = 0
        self.frames = []
        self.frame_count = 0
        self.overlay_text = ""
        self.original_frames = []
        
    def load_gif(self):
        file_path = filedialog.askopenfilename(filetypes=[("GIF files", "*.gif")])
        if file_path:
            try:
                self.gif = Image.open(file_path)
                self.frame_count = getattr(self.gif, 'n_frames', 1)
                self.original_frames = [frame.copy().convert("RGBA") for frame in self._iter_frames(self.gif)]
                self.frames = [ImageTk.PhotoImage(frame) for frame in self.original_frames]
                self.current_frame = 0
                self.show_frame()
                self.play_button.config(state=tk.NORMAL)
                self.add_text_button.config(state=tk.NORMAL)
                self.save_button.config(state=tk.NORMAL)
            except Exception as e:
                print(f"Error loading GIF: {e}", file=sys.stderr)
    
    def _iter_frames(self, im):
        try:
            i = 0
            while True:
                im.seek(i)
                yield im
                i += 1
        except EOFError:
            pass

    def show_frame(self):
        if self.frames:
            self.label.config(image=self.frames[self.current_frame])
        
    def toggle_play(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play()
        
    def play(self):
        if self.is_playing and self.frames:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.show_frame()
            self.master.after(100, self.play)  # Adjust delay as needed

    def add_text(self):
        self.overlay_text = simpledialog.askstring("Input", "Enter text to overlay:")
        if self.overlay_text:
            self.update_text()

    def update_text(self):
        if not self.overlay_text or not self.original_frames:
            return
        
        try:
            font_size = int(self.font_size_entry.get())
            pos_x = float(self.pos_x_entry.get())
            pos_y = float(self.pos_y_entry.get())
            
            if font_size <= 0 or pos_x < 0 or pos_x > 1 or pos_y < 0 or pos_y > 1:
                raise ValueError("Invalid input values")
        except ValueError as e:
            print(f"Error: {e}. Please enter valid numbers.", file=sys.stderr)
            return
        
        font = ImageFont.load_default().font_variant(size=font_size)
        
        for i, frame in enumerate(self.original_frames):
            new_frame = frame.copy()
            draw = ImageDraw.Draw(new_frame)
            
            left, top, right, bottom = font.getbbox(self.overlay_text)
            text_width = right - left
            text_height = bottom - top
            
            position = (int((new_frame.width - text_width) * pos_x), 
                        int((new_frame.height - text_height) * pos_y))
            
            # Draw text outline
            for offset in [(1,1), (-1,1), (1,-1), (-1,-1)]:
                draw.text((position[0]+offset[0], position[1]+offset[1]), self.overlay_text, font=font, fill=(255,255,255,255))
            
            # Draw main text
            draw.text(position, self.overlay_text, font=font, fill=(0,0,0,255))
            
            self.frames[i] = ImageTk.PhotoImage(new_frame)
        
        self.show_frame()

    def save_gif(self):
        if not self.frames:
            return
        
        save_path = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF files", "*.gif")])
        if save_path:
            try:
                frames_to_save = [ImageTk.getimage(frame) for frame in self.frames]
                frames_to_save[0].save(
                    save_path,
                    save_all=True,
                    append_images=frames_to_save[1:],
                    duration=100,
                    loop=0
                )
                print(f"GIF saved successfully to {save_path}")
            except Exception as e:
                print(f"Error saving GIF: {e}", file=sys.stderr)

root = tk.Tk()
app = GifViewer(root)
root.mainloop()