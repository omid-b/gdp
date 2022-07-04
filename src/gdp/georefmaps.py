#!/usr/bin/env python3

# Georeference maps and export GeoTIFFs using a WGS-84 coordinate system

import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, Toplevel
from PIL import Image, ImageTk

try:
    from osgeo import gdal, osr
except Exception as e:
    print(f"{e}. Hint: install and test GDAL.")
    print("install GDAL: $ pip install GDAL")
    print("   test GDAL: $ python3 -c 'from osgeo import gdal, osr'")
    exit(1)

pkg_dir, _ = os.path.split(__file__)

class Application(tk.Frame):
    def __init__(self, master=None, epsg=4326):
        super().__init__(master)
        window_size = [800, 600]
        icon_file = os.path.join(pkg_dir, 'data', 'world_icon.png')
        if os.path.isfile(icon_file):
            icon_img = ImageTk.PhotoImage(Image.open(icon_file))
            self.master.wm_iconphoto(False, icon_img)
        self.master.geometry(f"{window_size[0]}x{window_size[1]}")
        self.app_title = f"Georeference Maps (EPSG={epsg})"
        self.master.title(self.app_title)
        self.epsg = epsg
        self.pil_image = None
        self.canvas_cursor_xy = []
        self.warp_points = []
        self.create_menu()
        self.create_canvas()
        self.reset_transform()



    def create_menu(self):
        self.menu_bar = tk.Menu(self)
        self.file_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        self.gref_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        # file menu
        self.file_menu.add_command(label="Open image", command = self.file_menu_open_image, accelerator="Ctrl+O")
        if len(self.warp_points) >= 4:
            self.file_menu.add_command(label="Save GeoTIFF", command = self.file_menu_save_geotiff, accelerator="Ctrl+S", state="normal")
        else:
            self.file_menu.add_command(label="Save GeoTIFF", command = self.file_menu_save_geotiff, accelerator="Ctrl+S", state="disabled")
        self.menu_bar.bind_all("<Control-s>", self.file_menu_save_geotiff)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command = self.exit_program, accelerator="Ctrl+W")
        self.menu_bar.bind_all("<Control-o>", self.file_menu_open_image)
        self.menu_bar.bind_all("<Control-w>", self.exit_program )
        # georeferencing menu
        self.menu_bar.add_cascade(label="Georeferencing", menu=self.gref_menu)
        if len(self.warp_points):
            self.gref_menu.add_command(label="Remove last point", command = self.remove_last_point, accelerator="Ctrl+Z", state='normal')
            self.gref_menu.add_command(label="Remove all points", command = self.remove_all_points, accelerator="Ctrl+D", state='normal')
        else:
            self.gref_menu.add_command(label="Remove last point", command = self.remove_last_point, accelerator="Ctrl+Z", state='disabled')
            self.gref_menu.add_command(label="Remove all points", command = self.remove_all_points, accelerator="Ctrl+D", state='disabled')
        self.menu_bar.bind_all("<Control-z>", self.remove_last_point)
        self.menu_bar.bind_all("<Control-d>", self.remove_all_points)
        self.master.config(menu=self.menu_bar)


    def exit_program(self, event=None):
        self.master.destroy()


    def remove_last_point(self, event=None):
        if self.pil_image == None:
            return
        elif len(self.warp_points):
            self.warp_points.pop()
            self.create_menu()
            self.redraw_image()

    def remove_all_points(self, event=None):
        if self.pil_image == None:
            return
        elif len(self.warp_points):
            self.warp_points = []
            self.create_menu()
            self.redraw_image()

    def create_canvas(self):
        frame_statusbar = tk.Frame(self.master, bd=1, relief = tk.SUNKEN)
        self.label_image_info = tk.Label(frame_statusbar, text="image info", anchor=tk.E, padx = 5)
        self.label_image_pixel = tk.Label(frame_statusbar, text="(x, y)", anchor=tk.W, padx = 5)
        self.label_image_info.pack(side=tk.RIGHT)
        self.label_image_pixel.pack(side=tk.LEFT)
        frame_statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        # canvas properties
        self.canvas = tk.Canvas(self.master)
        self.canvas.pack(expand=True,  fill=tk.BOTH)

        self.canvas.bind("<Configure>", self.canvas_reset_size)
        # mouse wheel
        self.master.bind("<Motion>", self.mouse_motion) # mouse move
        self.master.bind("<Button-4>", self.canvas_zoom_in) # mouse wheel up
        self.master.bind("<Button-5>", self.canvas_zoom_out) # mouse wheel down
        # mouse LMB
        self.master.bind("<Button-1>", self.canvas_click)
        self.master.bind("<B1-Motion>", self.canvas_pan)
        self.master.bind("<Double-Button-1>", self.canvas_reset_size)

        self.master.bind("<Button-2>", self.canvas_click)
        self.master.bind("<B2-Motion>", self.canvas_pan)
        self.master.bind("<Double-Button-2>", self.canvas_reset_size)
        # mouse RMB
        self.master.bind("<Button-3>", self.canvas_right_click)

        self.master.bind("<KeyPress>", self.canvas_key_press)


    def file_menu_open_image(self, event=None):
        imagefile = tk.filedialog.askopenfilename(
            filetypes = [("Image file", ".bmp .BMP .png .PNG .jpg .JPG .jpeg .JPEG .tif .TIF .TIFF"), ("Bitmap", ".bmp .BMP"), ("PNG", ".png .PNG"), ("JPEG", ".jpg .jpeg .JPG .JPEG"), ("Tiff", ".tif .tiff .TIF .TIFF") ], 
            initialdir = os.getcwd()
            )
        self.warp_points = []
        self.set_image(imagefile)


    def file_menu_save_geotiff(self, event=None):
        if self.pil_image == None:
            return
        if len(self.warp_points) < 4:
            self.label_image_pixel["text"] = "Cannot save GeoTIFF file: at least 4 warp points are required!"
            return
        else:
            try:
                outfile = tk.filedialog.asksaveasfilename(
                    filetypes = [("Output GeoTIFF", ".tif"), ("Tiff", ".tif") ], 
                    initialdir = os.getcwd()
                    )
            except ValueError as e:
                tk.messagebox.showerror(title=None, message=f"{e}")
                return
            except TypeError as e:
                tk.messagebox.showerror(title=None, message=f"{e}")
                return

            if len(outfile) == 0:
                return
            elif outfile.split('.')[-1] != 'tif':
                tk.messagebox.showerror(title=None, message=f"Output file type error!\nIt must be *.tif")
                return

            try:
                self.pil_image.save(outfile, dpi=(300, 300))
                ds = gdal.Open(outfile, gdal.GA_Update)
                crs = osr.SpatialReference()
                crs.ImportFromEPSG(self.epsg)
                gcps = []
                for wp in self.warp_points:
                    gcps.append(gdal.GCP( float(wp[2]),float( wp[3]), 0.0,
                        float(wp[0]), float(wp[1]))
                    )
                ds.SetProjection(crs.ExportToWkt()) 
                ds.SetGCPs(gcps, crs.ExportToWkt())
                # close the output file 
                gdal.Warp(outfile, ds, dstSRS='EPSG:4326', format='gtiff')
                ds = None
                self.label_image_pixel["text"] = "GeoTIFF generated!"
                tk.messagebox.showinfo(title=None, message="GeoTIFF successfully generated!")
            except ValueError as e:
                tk.messagebox.showerror(title=None, message=f"ValueError:{e}")
                return
            except TypeError as e:
                tk.messagebox.showerror(title=None, message=f"TypeError:{e}")
                return
            except Exception as e:
                if os.path.isfile(outfile):
                    os.remove(outfile)
                tk.messagebox.showerror(title=None, message=f"Could not create the GeoTIFF!\nError:{e}")
                self.label_image_pixel["text"] = "Could not create the GeoTIFF!"


    def set_image(self, filename):
        if not filename:
            return
        self.pil_image = Image.open(filename)
        self.zoom_fit()
        self.draw_image(self.pil_image)
        self.master.title(self.app_title + " - " + os.path.basename(filename))
        self.label_image_info["text"] = f"{self.pil_image.format} : {self.pil_image.width} x {self.pil_image.height} {self.pil_image.mode}"
        os.chdir(os.path.dirname(filename))


    def draw_image(self, pil_image):
        if pil_image == None:
            return
        self.pil_image = pil_image
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        mat_inv = np.linalg.inv(self.mat_affine)
        affine_inv = (
            mat_inv[0, 0], mat_inv[0, 1], mat_inv[0, 2],
            mat_inv[1, 0], mat_inv[1, 1], mat_inv[1, 2]
        )
        dst = self.pil_image.transform(
            (canvas_width, canvas_height),
            Image.Transform.AFFINE,
            affine_inv,
            Image.Resampling.NEAREST
        )
        im = ImageTk.PhotoImage(image=dst)
        item = self.canvas.create_image(
            0, 0,
            anchor='nw',
            image=im
        )
        self.image = im
        for i, wp in enumerate(self.warp_points, start=1):
            if i == len(self.warp_points):
                fill_color = "#dd0000"
            else:
                fill_color = "#00dd00"
            image_x0 = self.mat_affine[0][2]
            image_y0 = self.mat_affine[1][2]
            wp_canvas_x = self.mat_affine[0][2] + wp[0] * self.mat_affine[0][0]
            wp_canvas_y = self.mat_affine[1][2] + wp[1] * self.mat_affine[1][1]

            self.canvas.create_line(wp_canvas_x-7, wp_canvas_y, wp_canvas_x-2, wp_canvas_y, fill=fill_color, width= 3)
            self.canvas.create_line(wp_canvas_x+7, wp_canvas_y, wp_canvas_x+2, wp_canvas_y, fill=fill_color, width= 3)
            self.canvas.create_line(wp_canvas_x, wp_canvas_y-7, wp_canvas_x, wp_canvas_y-2, fill=fill_color, width= 3)
            self.canvas.create_line(wp_canvas_x, wp_canvas_y+7, wp_canvas_x, wp_canvas_y+2, fill=fill_color, width= 3)
            self.canvas.create_text(wp_canvas_x, wp_canvas_y-15, text=f"({float(wp[2])}, {float(wp[3])})", fill=fill_color, font=('Helvetica 16 bold'))



    def redraw_image(self):
        if self.pil_image == None:
            return
        self.draw_image(self.pil_image)


    def zoom_fit(self, event=None):
        if self.pil_image == None:
            return
        image_width = self.pil_image.width
        image_height = self.pil_image.height
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if (image_width * image_height <= 0) or (canvas_width * canvas_height <= 0):
            return
        self.reset_transform()
        scale = 1.0
        offsetx = 0.0
        offsety = 0.0
        if (canvas_width * image_height) > (image_width * canvas_height):
            scale = canvas_height / image_height
            offsetx = (canvas_width - image_width * scale) / 2
        else:
            scale = canvas_width / image_width
            offsety = (canvas_height - image_height * scale) / 2
        self.scale(scale)
        self.translate(offsetx, offsety)


    def translate(self, offset_x, offset_y):
        mat = np.eye(3)
        mat[0, 2] = float(offset_x)
        mat[1, 2] = float(offset_y)
        self.mat_affine = np.dot(mat, self.mat_affine)


    def scale(self, scale:float):
        mat = np.eye(3)
        mat[0, 0] = scale
        mat[1, 1] = scale
        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale_image(self, scale:float, cx:float, cy:float):
        self.translate(-cx, -cy)
        self.scale(scale)
        self.translate(cx, cy)

    def reset_transform(self):
        self.mat_affine = np.eye(3)

    # mouse events

    def mouse_motion(self, event):
        if (self.pil_image == None):
            return
        self.master.config(cursor="")
        image_xy = self.get_image_xy(event.x, event.y)
        if len(image_xy):
            self.label_image_pixel["text"] = (f"({image_xy[0]:.2f}, {image_xy[1]:.2f})")
        else:
            self.label_image_pixel["text"] = ("(--, --)")
        self.canvas_cursor_xy = [event.x, event.y]


    def get_image_xy(self, canvas_x, canvas_y):
        if self.pil_image == None:
            return []
        mat_inv = np.linalg.inv(self.mat_affine)
        image_xy = np.dot(mat_inv, (canvas_x, canvas_y, 1.)).tolist()[0:2]
        if  image_xy[0] < 0 or image_xy[1] < 0 or image_xy[0] > self.pil_image.width or image_xy[1] > self.pil_image.height:
            return []
        return image_xy

    def get_canvas_xy(self, image_x, image_y):
        # canvas_xy = np.dot(self.mat_affine, (image_x, image_y, 1.)).tolist()[0:2]
        canvas_xy = [self.canvas.winfo_width(), self.canvas.winfo_height()]
        return canvas_xy


    def canvas_right_click(self, event):
        if (self.pil_image == None):
            return
        image_xy = self.get_image_xy(event.x, event.y)
        if len(image_xy):
            self.add_warp_point_dialog(image_xy[0], image_xy[1])

    def canvas_key_press(self, event):
        if (self.pil_image == None):
            return
        event.x = self.canvas_cursor_xy[0]
        event.y = self.canvas_cursor_xy[1]
        if event.char == ']':
            self.canvas_zoom_in(event)
        elif event.char == '[':
            self.canvas_zoom_out(event)
        elif event.char == 'p':
            self.canvas_right_click(event)
        else:
            return
    

    def add_warp_point_dialog(self, image_x, image_y):
        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
        warp_window = tk.Toplevel(self.master)
        warp_window.title(f" ")
        main_size = [self.master.winfo_width(), self.master.winfo_height()]
        main_position = [self.master.winfo_x(), self.master.winfo_y()]
        this_size = [300, 150]
        this_position = [int(main_position[0] + (main_size[0])/2 - this_size[0]/2),
                         int(main_position[1] + (main_size[1])/2 - this_size[1]/2) ]
        warp_window.geometry(f"{this_size[0]}x{this_size[1]}+{this_position[0]}+{this_position[1]}")
        warp_window.resizable(0,0)

        lbl_xy_info = tk.Label(warp_window, 
            text =f"Point #{len(self.warp_points)+1}:  (x, y) = ({image_x:.0f}, {image_y:.0f}) ")
        lbl_lon = tk.Label(warp_window, text ="longitude: ")
        lbl_lat = tk.Label(warp_window, text ="latitude: ")

        vcmd_lon = (self.register(self.islon), '%P')
        vcmd_lat = (self.register(self.islat), '%P')
        self.ent_lon = tk.Entry(warp_window, width=10, justify='center',
                           validate="all", validatecommand=vcmd_lon )
        self.ent_lat = tk.Entry(warp_window, width=10, justify='center',
                           validate="all", validatecommand=vcmd_lat )
        btn_cancel = tk.Button(warp_window, text = "Cancel",
                               command= lambda: self.destroy_add_warp_win(warp_window))
        self.btn_add_warp = tk.Button(warp_window, text = "Add", state='disabled',
                                      command= lambda: self.btn_add_warp_clicked(image_x, image_y))

        lbl_xy_info.grid(row=0, column=0, pady=5, padx=10, columnspan=3, sticky="W")
        lbl_lon.grid(row=1, column=0, pady=5, padx=10, sticky="W")
        lbl_lat.grid(row=2, column=0, pady=5, padx=10, sticky="W")
        self.ent_lon.grid(row=1, column=1, pady=5, padx=5, columnspan=2, sticky="E")
        self.ent_lat.grid(row=2, column=1, pady=5, padx=5, columnspan=2, sticky="E")
        btn_cancel.grid(row=3, column=1, pady=5, padx=5, sticky="E")
        self.btn_add_warp.grid(row=3, column=2, pady=5, padx=5, sticky="E")


    def btn_add_warp_clicked(self, image_x, image_y):
        new_warp_lon = self.ent_lon.get()
        new_warp_lat = self.ent_lat.get()
        self.warp_points.append([image_x, image_y, new_warp_lon, new_warp_lat])
        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
        self.create_menu()
        self.redraw_image()


    def destroy_add_warp_win(self, warp_window):
        warp_window.destroy()


    def islon(self, val):
        if len(val) == 0 or val == '-':
            self.btn_add_warp["state"] = "disabled"
            return True
        else:
            try:
                val = float(val)
                if val >= -180 and val <= 180:
                    if len(self.ent_lon.get()) and self.ent_lat.get():
                        self.btn_add_warp["state"] = "normal"
                    return True
                else:
                    self.btn_add_warp["state"] = "disabled"
                    return False
            except:
                self.btn_add_warp["state"] = "disabled"
                return False


    def islat(self, val):
        if len(val) == 0 or val == '-':
            self.btn_add_warp["state"] = "disabled"
            return True
        else:
            try:
                val = float(val)
                if val >= -90 and val <= 90:
                    if len(self.ent_lon.get()) and self.ent_lat.get():
                        self.btn_add_warp["state"] = "normal"
                    return True
                else:
                    self.btn_add_warp["state"] = "disabled"
                    return False
            except:
                self.btn_add_warp["state"] = "disabled"
                return False



    def canvas_click(self, event): # left/middle mouse button click
        self.__old_event = event


    def canvas_pan(self, event): # left/middle mouse button drag
        if (self.pil_image == None):
            return
        self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self.redraw_image()
        self.master.config(cursor="fleur")
        self.__old_event = event


    def canvas_reset_size(self, event):
        if self.pil_image == None:
            return
        self.zoom_fit()
        self.redraw_image()


    def canvas_zoom_in(self, event):
        if self.pil_image == None:
            return
        self.scale_image(1.25, event.x, event.y)
        self.redraw_image()


    def canvas_zoom_out(self, event):
        if self.pil_image == None:
            return
        self.scale_image(0.75, event.x, event.y)
        self.redraw_image()


    def exit(self):
        self.master.destroy() 

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
