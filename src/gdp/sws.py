#!/usr/bin/env python3

import os
import numpy as np
import tkinter as tk
import tkinter.messagebox

import matplotlib

import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg
import seaborn as sns

from gdp import sacproc


class SWS_Dataset_App(tk.Frame):
    def __init__(self, sacfiles_info, time_range=None, master=None):
        super().__init__(master)
        matplotlib.rcParams["savefig.directory"] = os.getcwd()
        matplotlib.use("TkAgg")
        matplotlib.backend_bases.NavigationToolbar2.toolitems = (
            ('Home', 'Reset original view', 'home', 'home'),
            (None, None, None, None),
            (None, None, None, None),
            ('Pan', 'Pan timeseries (hold X)', 'move', 'pan'),
            ('Zoom', 'Zoom timeseries (hold X)', 'zoom_to_rect', 'zoom'),
            (None, None, None, None),
            ('Save', 'Save the figure', 'filesave', 'save_figure'),
        )
        self.master = master
        self.master.config(bg='#fff')
        self.win_width = 1000
        self.win_height = 650

        self.plot_data_index = 0

        # build shear-wave-splitting dataset dictionary
        self.sacfiles_info = sacfiles_info
        self.sws_dataset = self.get_sws_dataset()
        self.plot_datalist = self.get_plot_datalist()

        num_events = len(self.sws_dataset.keys())
        self.num_measurements = len(self.plot_datalist)
        num_sacs = len(self.plot_datalist) * 3

        self.master.geometry(f"{self.win_width}x{self.win_height}")
        self.app_title = f"SWS Dataset QC - #Events: {num_events} - #Three component data: {self.num_measurements}"
        self.master.title(self.app_title)
        self.state_modified = False
        self.create_ui()

        if num_sacs != len(sacfiles_info.keys()):
            self.show_duplication_warning()
            self.lbl_statusbar["text"] = "Warning! Some data dplication was found."
        else:
            self.lbl_statusbar["text"] = "Ready..."

    def create_ui(self):
        self.create_menu()
        self.create_main()


    def create_menu(self):
        self.menu_bar = tk.Menu(self)
        self.file_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        self.gref_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        # file menu
        if self.state_modified:
            self.file_menu.add_command(label="Apply changes", command = self.apply_changes, accelerator="Ctrl+S", state="normal")
        else:
            self.file_menu.add_command(label="Apply changes", command = self.apply_changes, accelerator="Ctrl+S", state="disabled")
        self.menu_bar.bind_all("<Control-s>", self.apply_changes)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command = self.exit_program, accelerator="Ctrl+W")
        self.menu_bar.bind_all("<Control-w>", self.exit_program)
        ### TEST ###
        self.menu_bar.bind_all("<Control-m>", self.next_data)
        self.menu_bar.bind_all("<Control-n>", self.prev_data)
        ############
        self.master.config(menu=self.menu_bar)


    def next_data(self, event=None):
        if self.plot_data_index >= (self.num_measurements - 1):
            return
        self.plot_data_index += 1
        print(self.plot_data_index)
        self.update_canvas()


    def prev_data(self, event=None):
        if self.plot_data_index == 0:
            return
        self.plot_data_index -= 1
        print(self.plot_data_index)
        self.update_canvas()


    def create_main(self):
        # create container for plot
        canvas_width = self.win_width
        canvas_height = self.win_height
        self.frame_plot = tk.Frame(self.master)
        self.frame_plot.pack(side=tk.TOP)
        self.canvas = self.create_canvas()
        self.canvas_toolbar = tkagg.NavigationToolbar2Tk(self.canvas, self.frame_plot, pack_toolbar=False)
        for x in self.canvas_toolbar.winfo_children():
            x.config(bg='#fff')
        self.canvas_toolbar._message_label.config(bg='#fff')
        self.canvas_toolbar._message_label.config(fg='#000')
        self.canvas_toolbar.config(bg='#fff')
    

        self.update_canvas()
        self.canvas_toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)



        # statusbar
        frame_statusbar = tk.Frame(self.master, bd=1, relief = tk.SUNKEN)
        self.lbl_statusbar = tk.Label(frame_statusbar, text="", anchor=tk.E, padx = 5)
        self.lbl_statusbar.pack(side=tk.LEFT)
        frame_statusbar.pack(side=tk.BOTTOM, fill=tk.X)


    def create_canvas(self):
        sns.set_context('notebook')
        sns.set_style('white')

        self.fig = plt.Figure(dpi=72, figsize=(10,8))
        self.ax1 = self.fig.add_subplot(311)
        self.ax2 = self.fig.add_subplot(312)
        self.ax3 = self.fig.add_subplot(313)
        self.ax1.get_shared_x_axes().join(self.ax1, self.ax2, self.ax3)
        plt.close()
        canvas = tkagg.FigureCanvasTkAgg(self.fig , master=self.frame_plot)
        return canvas

        

    def update_canvas(self, event=None):
        # clear axis
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        # plot timeseries
        plot_data = self.plot_datalist[self.plot_data_index]
        self.ax1.plot(plot_data[0]['times'], plot_data[0]['data'], color='#2874A6', linewidth=1)
        self.ax2.plot(plot_data[1]['times'], plot_data[1]['data'], color='#2874A6', linewidth=1)
        self.ax3.plot(plot_data[2]['times'], plot_data[2]['data'], color='#2874A6', linewidth=1)
        # set axis limits and ticks
        self.ax1.set_xticks([],[])
        self.ax2.set_xticks([],[])
        self.ax1.autoscale_view()
        self.ax2.autoscale_view()
        self.ax3.autoscale_view()
        ax1_ylim = self.ax1.get_ylim()
        ax2_ylim = self.ax2.get_ylim()
        ax3_ylim = self.ax3.get_ylim()
        self.ax1.set_ylim([ax1_ylim[0], 1.3*ax1_ylim[1]])
        self.ax2.set_ylim([ax2_ylim[0], 1.3*ax2_ylim[1]])
        self.ax3.set_ylim([ax3_ylim[0], 1.3*ax3_ylim[1]])
        # set titles
        self.ax1.set_title(f"{plot_data[0]['kstnm']}.{plot_data[0]['kcmpnm']}")
        self.ax2.set_title(f"{plot_data[1]['kstnm']}.{plot_data[1]['kcmpnm']}")
        self.ax3.set_title(f"{plot_data[2]['kstnm']}.{plot_data[2]['kcmpnm']}")
        self.ax3.set_xlabel("Time (s)")

        # plot event origin
        tt_color = '#888'
        self.ax1.plot([plot_data[0]['o'], plot_data[0]['o']], ax1_ylim, color=tt_color, linestyle='dotted', linewidth=2)
        self.ax2.plot([plot_data[1]['o'], plot_data[1]['o']], ax2_ylim, color=tt_color, linestyle='dotted', linewidth=2)
        self.ax3.plot([plot_data[2]['o'], plot_data[2]['o']], ax3_ylim, color=tt_color, linestyle='dotted', linewidth=2)
        bbox_props = dict(facecolor='white', alpha=0.5)
        self.ax1.text(plot_data[0]['o'], ax1_ylim[1]*1.2, 'O', fontsize=12, color=tt_color,
        verticalalignment='top',horizontalalignment='center', bbox=bbox_props)
        self.ax2.text(plot_data[1]['o'], ax2_ylim[1]*1.2, 'O', fontsize=12, color=tt_color,
        verticalalignment='top',horizontalalignment='center', bbox=bbox_props)
        self.ax3.text(plot_data[2]['o'], ax3_ylim[1]*1.2, 'O', fontsize=12, color=tt_color,
        verticalalignment='top',horizontalalignment='center', bbox=bbox_props)

        # plot travel times
        for x in [1000, 1500, 2000]:
            self.ax1.plot([x, x], ax1_ylim, color=tt_color, linestyle='dashed', linewidth=2)
            self.ax2.plot([x, x], ax2_ylim, color=tt_color, linestyle='dashed', linewidth=2)
            self.ax3.plot([x, x], ax3_ylim, color=tt_color, linestyle='dashed', linewidth=2)
            self.ax1.text(x, ax1_ylim[1]*1.2, 'Pdiff', fontsize=12, color=tt_color,
            verticalalignment='top',horizontalalignment='center', bbox=bbox_props)
            self.ax2.text(x, ax2_ylim[1]*1.2, 'Pdiff', fontsize=12, color=tt_color,
            verticalalignment='top',horizontalalignment='center', bbox=bbox_props)
            self.ax3.text(x, ax3_ylim[1]*1.2, 'Pdiff', fontsize=12, color=tt_color,
            verticalalignment='top',horizontalalignment='center', bbox=bbox_props)

        self.canvas.draw()
        self.canvas.flush_events()
        self.canvas.get_tk_widget().pack()
        self.canvas_toolbar.update()
        plt.close()


    def show_duplication_warning(self):
        duplicates = self.find_duplicates()
        duplicates = '\n'.join(duplicates)
        message = f"These sac files will be ignored:\n\n{duplicates}"
        tkinter.messagebox.showinfo(title="Data duplication!", message=message)


    def find_duplicates(self):
        inp_datalist = list(self.sacfiles_info.keys())
        sws_datalist = []
        for event in self.sws_dataset.keys():
            for station in self.sws_dataset[event].keys():
                for channel in ['N','E','Z']:
                    sacfiles = list(self.sws_dataset[event][station][channel].keys())
                    sws_datalist.append(sacfiles[0])
        duplicates = []
        for sacfile in inp_datalist:
            if sacfile not in sws_datalist:
                duplicates.append(f"'{os.path.basename(sacfile)}'")
        return duplicates

    def get_plot_datalist(self):
        plot_datalist = []
        for event in self.sws_dataset.keys():
            for station in self.sws_dataset[event].keys():
                data_trio = []
                for channel in ['N','E','Z']:
                    sacfile_key = list(self.sws_dataset[event][station][channel].keys())[0]
                    data_trio.append(self.sws_dataset[event][station][channel][sacfile_key])
                plot_datalist.append(data_trio)
        return plot_datalist


    def get_sws_dataset(self):
        sws_dataset = {}
        # find uniq list of events
        events_uniq = []
        # reverse sorting keys: I prefer BHN over BH1, for example
        for key in sorted(self.sacfiles_info.keys(), reverse=True):
            event_dir, sacfile = os.path.split(key)
            kstnm = self.sacfiles_info[key]['kstnm']
            kcmpnm = self.sacfiles_info[key]['kcmpnm']
            if kcmpnm in ["BHN","HHN","BH1","HH1"]:
                channel = 'N'
            elif kcmpnm in ["BHE","HHE","BH2","HH2"]:
                channel = 'E'
            elif kcmpnm in ["BHZ","HHZ"]:
                channel = 'Z'
            else:
                continue
            # build dict structure
            if event_dir not in sws_dataset.keys():
                sws_dataset[event_dir] = {}
            if kstnm not in sws_dataset[event_dir].keys():
                sws_dataset[event_dir][kstnm] = {}
            if channel not in sws_dataset[event_dir][kstnm].keys():
                sws_dataset[event_dir][kstnm][channel] = {}
            # append to lists
            sws_dataset[event_dir][kstnm][channel][key] = self.sacfiles_info[key]
        # delete station if data for a channel is missing
        for event in sws_dataset.keys():
            for station in sws_dataset[event].keys():
                del_station = False
                for channel in ['N','E','Z']:
                    if channel not in sws_dataset[event][station].keys():
                        del_station = True
                        continue
                    elif len(sws_dataset[event][station][channel].keys()) == 0:
                        del_station = True
                        continue
                if del_station:
                    del sws_dataset[event][station]
            if len(sws_dataset[event]) == 0:
                del sws_dataset[event]
        return sws_dataset

    
    def exit_program(self, event=None):
        self.master.destroy()

    def apply_changes(self, event=None):
        pass


def run_sws_dataset_app(sacfiles):
    root = tk.Tk()
    sacfiles_info = sacproc.get_sacfiles_info(sacfiles, read_headers=True, read_data=True)
    app = SWS_Dataset_App(sacfiles_info, master=root)
    app.mainloop()
    # import gi
    # gi.require_version('Gtk', '3.0')
    # from gi.repository import Gtk

    # from matplotlib.figure import Figure
    # from matplotlib.backends.backend_gtk3agg import FigureCanvas
    # from matplotlib.backends.backend_gtk3 import (
    #     NavigationToolbar2GTK3 as NavigationToolbar)

    # win = Gtk.Window()
    # win.connect("destroy", lambda x: Gtk.main_quit())
    # win.set_default_size(400,300)
    # win.set_title("Embedding in GTK")

    # vbox = Gtk.VBox()
    # win.add(vbox)

    # fig = Figure(figsize=(5,4), dpi=100)
    # ax = fig.add_subplot(111)
    # ax.plot([1,2,3])

    # canvas = FigureCanvas(fig)  # a Gtk.DrawingArea
    # vbox.pack_start(canvas, True, True, 0)
    # toolbar = NavigationToolbar(canvas, win)
    # vbox.pack_start(toolbar, False, False, 0)

    # win.show_all()
    # Gtk.main()


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        print("Error! Must enter <sacfiles> as sys.argv[1]!")
        exit(1)
    
    root = tk.Tk()
    sacfiles_info = sacproc.get_sacfiles_info(sys.argv[1:], read_headers=True, read_data=True)
    app = SWS_Dataset_App(sacfiles_info, master=root)
    app.mainloop()



