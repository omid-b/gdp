#!/usr/bin/env python3

import os
import shutil
import numpy as np
import tkinter as tk
import tkinter.messagebox
from tkinter import font

import operator
from copy import deepcopy

from datetime import datetime
import matplotlib

import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
import matplotlib.backends.backend_tkagg as tkagg
import seaborn as sns

from . import sacproc
from . import dependency

class SWS_Dataset_App(tk.Frame):
    def __init__(self, sacfiles_info, master=None,
        refmodel='iasp91', SAC='auto', headonly=False):
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

        self.defaultFont = font.nametofont("TkDefaultFont")
        self.menuFont = font.nametofont("TkMenuFont")
        self.menuFont.configure(family="Dejavu",
                                   size=10,
                                   weight=font.NORMAL)
        self.defaultFont.configure(family="Dejavu",
                                   size=11,
                                   weight=font.NORMAL)

        self.master = master
        self.refmodel = refmodel
        self.SAC = SAC

        self.master.config(bg='#fff')
        self.win_width = 1000
        self.win_height = 700
        self.plot_data_index = 0

        # build required dictionaries and lists
        self.sacfiles_info = sacfiles_info
        print("Calculate theoretical travel times ...")
        self.sws_dataset = self.get_sws_dataset()

        duplicates = self.find_duplicates()
        if len(duplicates):
            duplicates = '\n'.join(duplicates)
            print(f"WARNING! Some data files are ignored:\n{duplicates}")

        if len(self.sws_dataset) == 0:
            print("Error! This dataset does not include any complete-set 3-component timeseries!")
            exit(1)

        print(f"Write arrivals into headers (model={refmodel})...")
        self.write_traveltime_headers()
        
        if headonly:
            print("Headers were successfully updated.")
            exit(0)

        self.old_select_status = self.get_select_status()
        self.current_select_status = self.get_select_status()
        self.plot_datalist = self.get_plot_datalist()

        num_events = len(self.sws_dataset.keys())
        self.num_measurements = len(self.plot_datalist)

        self.master.geometry(f"{self.win_width}x{self.win_height}")
        self.master.minsize(self.win_width, self.win_height)
        self.app_title = f"SWS Dataset QC - #Events: {num_events} - #Three component data: {self.num_measurements}"
        self.master.title(self.app_title)
        self.init_ui()

        if len(duplicates):
            self.lbl_statusbar["text"] = "Warning! Some data duplication was found."
            self.show_duplication_warning()
        else:
            self.lbl_statusbar["text"] = "Ready..."



    def write_traveltime_headers(self):
        # store T1-T9 and KT1-KT2
        for event in self.sws_dataset.keys():
            for station in self.sws_dataset[event].keys():
                headers = {}
                iP = 1
                for p_phase in self.sws_dataset[event][station]['P'].keys():
                    if iP <= 2:
                        headers[f"T{iP}"] = self.sws_dataset[event][station]['P'][p_phase][0]
                        headers[f"KT{iP}"] = p_phase
                        iP += 1
                iS = 3
                for s_phase in self.sws_dataset[event][station]['S'].keys():
                    if iS <= 4 and s_phase not in ['SKKS', 'PKS']:
                        headers[f"T{iS}"] = self.sws_dataset[event][station]['S'][s_phase][0]
                        headers[f"KT{iS}"] = s_phase
                        iS += 1
                iS = 5
                for s_phase in self.sws_dataset[event][station]['S'].keys():
                    if s_phase in ['SKKS', 'PKS']:
                        headers[f"T{iS}"] = self.sws_dataset[event][station]['S'][s_phase][0]
                        headers[f"KT{iS}"] = s_phase
                        iS += 1
                arrivals_saved = []
                for key in headers.keys():
                    if key[0] == 'K':
                        arrivals_saved.append(headers[key])
                i=7
                for p_phase in self.sws_dataset[event][station]['P'].keys():
                    if i <= 9 and p_phase not in arrivals_saved:
                        headers[f"T{i}"] = self.sws_dataset[event][station]['P'][p_phase][0]
                        headers[f"KT{i}"] = p_phase
                        i += 1
                for s_phase in self.sws_dataset[event][station]['S'].keys():
                    if i <= 9 and s_phase not in arrivals_saved:
                        headers[f"T{i}"] = self.sws_dataset[event][station]['S'][s_phase][0]
                        headers[f"KT{i}"] = s_phase
                        i += 1
                # write T1-T9 and KT1-KT2 headers into the three components
                if self.SAC == 'auto':
                    self.SAC = dependency.find_sac_path()
                if len(self.SAC) == 0 or not os.path.isfile(self.SAC):
                    print("Error! Could not find SAC software in the following path:\n{SAC}\n")
                    exit(1)
                for comp in ['N','E','Z']:
                    sacfile = list(self.sws_dataset[event][station][comp].keys())[0]
                    sacproc.write_sac_headers(sacfile, headers, SAC=self.SAC)



    def get_select_status(self):
        select_status = []
        for event in self.sws_dataset.keys():
            for station in self.sws_dataset[event].keys():
                for p_phase in self.sws_dataset[event][station]['P'].keys():
                    select_status.append(self.sws_dataset[event][station]['P'][p_phase][1])
                for s_phase in self.sws_dataset[event][station]['S'].keys():
                    select_status.append(self.sws_dataset[event][station]['S'][s_phase][1])
        return select_status

    def get_select_status_index(self, measurement_index):
        current_index = 0
        select_status_index = 0
        for event in self.sws_dataset.keys():
            for station in self.sws_dataset[event]:
                if current_index == measurement_index:
                    return select_status_index
                else:
                    select_status_index += len(self.sws_dataset[event][station]['P'].keys()) \
                                         + len(self.sws_dataset[event][station]['S'].keys())
                current_index += 1



    def init_ui(self):
        self.create_menu()
        self.create_main()
        self.master.bind('<Right>', self.next_data)
        self.master.bind('<Left>', self.prev_data)


    def create_menu(self):
        self.menu_bar = tk.Menu(self)
        self.file_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        self.gref_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        # file menu
        self.update_menu = self.file_menu.add_command(label="Update datasets",
            command=self.apply_update_dataset, accelerator="Ctrl+S")
        self.menu_bar.bind_all("<Control-s>", self.apply_update_dataset )
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command = self.exit_program,
            accelerator="Ctrl+W")
        self.menu_bar.bind_all("<Control-w>", self.exit_program)
        self.master.config(menu=self.menu_bar)


    def next_data(self, event=None):
        if self.plot_data_index >= (self.num_measurements - 1):
            return
        self.plot_data_index += 1
        self.update_info()
        self.update_buttons()
        self.update_arrivals()
        self.update_canvas()


    def prev_data(self, event=None):
        if self.plot_data_index == 0:
            return
        self.plot_data_index -= 1
        self.update_info()
        self.update_buttons()
        self.update_arrivals()
        self.update_canvas()


    def create_main(self):
        # create canvas frame
        canvas_relx = 0
        canvas_rely = 0
        canvas_relwidth = 0.75
        canvas_relheight = 1
        self.frm_canvas = tk.Frame(self.master, bg='#fff')
        self.frm_canvas.place(relx=canvas_relx, rely=canvas_rely,
            relwidth=canvas_relwidth, relheight=canvas_relheight)
        self.canvas = self.create_canvas()
        self.canvas_toolbar = tkagg.NavigationToolbar2Tk(self.canvas,
            self.frm_canvas, pack_toolbar=False)
        for x in self.canvas_toolbar.winfo_children():
            x.config(bg='#fff')
        self.canvas_toolbar._message_label.config(bg='#fff')
        self.canvas_toolbar._message_label.config(fg='#000')
        self.canvas_toolbar.config(bg='#fff')
        self.canvas_toolbar.place(relx=0.1, rely=0,
            relwidth=canvas_relwidth, relheight=0.08)
        self.update_canvas()

        # create information frame
        canvas_relwidth -= 0.02
        frm_info_relheight = 0.2
        self.frm_info = tk.Frame(self.master, bg='#fff')
        self.frm_info.place(relx=canvas_relwidth, rely=0.1,
            relwidth=(1-canvas_relwidth), relheight=frm_info_relheight)
        self.update_info()

        # create arrivals frame
        frm_arrivals_relheight = 0.45
        self.frm_arrivals = tk.Frame(self.master, bg='#fff')
        self.frm_arrivals.place(relx=canvas_relwidth, rely=0.1+frm_info_relheight,
            relwidth=(1-canvas_relwidth), relheight=frm_arrivals_relheight)
        self.update_arrivals()
        

        # create control buttons frame
        self.frm_buttons = tk.Frame(self.master, bg='#fff')
        self.frm_buttons.place(relx=canvas_relwidth,
            rely=0.1+frm_info_relheight+frm_arrivals_relheight,
            relwidth=(1-canvas_relwidth),
            relheight=(0.8-frm_arrivals_relheight-frm_info_relheight))
        self.btn_update = tk.Button(self.frm_buttons, text="Update SWS dataset",
            bd=1, relief=tk.RAISED, font='Dejavu 11 bold', command=self.apply_update_dataset)
        self.btn_prev = tk.Button(self.frm_buttons, text="Previous",
            bd=1, relief=tk.RAISED, font='Dejavu 11', command=self.prev_data)
        self.btn_next = tk.Button(self.frm_buttons, text="Next",
            bd=1, relief=tk.RAISED, font='Dejavu 11', command=self.next_data)
        self.btn_update.place(relx=0, rely=0.1, relwidth=0.8, relheight=0.33)
        self.btn_prev.place(relx=0, rely=0.66, relwidth=0.37, relheight=0.33)
        self.btn_next.place(relx=0.43, rely=0.66, relwidth=0.37, relheight=0.33)
        self.update_buttons()


        # statusbar
        frame_statusbar = tk.Frame(self.master, bd=1, relief = tk.SUNKEN)
        self.lbl_statusbar = tk.Label(frame_statusbar, text="", anchor=tk.E, padx = 5)
        self.lbl_statusbar.pack(side=tk.LEFT)
        frame_statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_buttons(self):
        self.btn_update.config(state='disabled')
        self.file_menu.entryconfig("Update datasets", state="disabled")
        for i in range(len(self.current_select_status)):
            if self.current_select_status[i] != self.old_select_status[i]:
                self.btn_update.config(state='normal')
                self.file_menu.entryconfig("Update datasets", state="normal")
                break

        if self.plot_data_index == 0:
            self.btn_prev.config(state='disabled')
        else:
            self.btn_prev.config(state='normal')

        if self.plot_data_index == (self.num_measurements - 1):
            self.btn_next.config(state='disabled')
        else:
            self.btn_next.config(state='normal')



    def update_arrivals(self):
        plot_data = self.plot_datalist[self.plot_data_index]
        # update plot_data[3] and plot_data[4]
        p_phase_names = list(plot_data[3].keys())
        s_phase_names = list(plot_data[4].keys())
        num_p_phases = len(p_phase_names)
        num_s_phases = len(s_phase_names)
        p_index_start = self.get_select_status_index(self.plot_data_index)
        p_index_end = p_index_start + num_p_phases
        s_index_start = p_index_end
        s_index_end = s_index_start + num_s_phases
        select_status = []
        for x in self.current_select_status[p_index_start:s_index_end]:
            select_status.append(x)

        i = 0
        for p_phase in p_phase_names:
            plot_data[3][p_phase][1] = select_status[i]
            i += 1
        for s_phase in s_phase_names:
            plot_data[4][s_phase][1] = select_status[i]
            i += 1

        for widget in self.frm_arrivals.winfo_children():
            widget.destroy()
        lbl_info = tk.Label(self.frm_arrivals, text=f"Theoretical arrivals ({self.refmodel}):",
            justify=tk.LEFT, font='Dejavu 11 bold', bg='#fff', fg='#000')
        lbl_info.place(relx=0, rely=0)

        self.chb_vars = [tk.IntVar() for x in range(num_p_phases + num_s_phases)]
        for iP, p_phase_name in enumerate(p_phase_names):
            var = self.chb_vars[iP]
            chb = tk.Checkbutton(self.frm_arrivals, text=f"{p_phase_name}",
                onvalue=1, offvalue=0,
                bg='white', fg='#000', activebackground='white',
                activeforeground='#555',selectcolor="white", bd=0, highlightthickness=0,
                font='Dejavu 11', justify=tk.LEFT,
                command=self.update_select_status,
                variable=var)
            if select_status[iP]:
                chb.select()
            else:
                chb.deselect()
            chb.place(relx=0, rely=iP*0.07 + 0.1)


        for iS, s_phase_name in enumerate(s_phase_names):
            var = self.chb_vars[iS + num_p_phases]
            chb = tk.Checkbutton(self.frm_arrivals, text=f"{s_phase_name}",
                onvalue=1, offvalue=0,
                bg='white', fg='#000', activebackground='white',
                activeforeground='#555',selectcolor="white", bd=0, highlightthickness=0,
                font='Dejavu 11', justify=tk.LEFT,
                command=self.update_select_status,
                variable=var)
            if select_status[iS+num_p_phases]:
                chb.select()
            else:
                chb.deselect()
            chb.place(relx=0.4, rely=iS*0.07 + 0.1)




    def update_select_status(self):
        select_status = []
        for i, widget in enumerate(self.frm_arrivals.winfo_children()[1:]):
            select_status.append(self.chb_vars[i].get())
        select_status_index_start = self.get_select_status_index(self.plot_data_index)
        select_status_index_end = select_status_index_start + len(select_status)
        i = 0
        for j in range(select_status_index_start, select_status_index_end):
            self.old_select_status[j] = self.current_select_status[j]
            self.current_select_status[j] = select_status[i]
            i += 1
        self.update_canvas()
        self.update_buttons()


    def update_info(self):
        for widget in self.frm_info.winfo_children():
            widget.destroy()
        plot_data = self.plot_datalist[self.plot_data_index]
        lbl_info = tk.Label(self.frm_info, text=f"Event: {plot_data[2]['event']}\n\nData information ({self.plot_data_index+1} of {self.num_measurements}):",
            justify=tk.LEFT, font='Dejavu 11 bold', bg='#fff', fg='#000')
        lbl_info.place(relx=0, rely=0)
        col1_text = f"Network: {plot_data[2]['knetwk']}\n\nStation: {plot_data[2]['kstnm']}"
        col2_text = "BAZ: %.2f\n\nGCARC: %.2f" %(float(plot_data[2]['baz']), float(plot_data[2]['gcarc']))
        lbl_col1 = tk.Label(self.frm_info, bg='#fff', fg='#000',  justify=tk.LEFT, text=col1_text, font='Dejavu 11')
        lbl_col2 = tk.Label(self.frm_info, bg='#fff', fg='#000', justify=tk.LEFT, text=col2_text, font='Dejavu 11')
        lbl_col1.place(relx=0, rely=0.5)
        lbl_col2.place(relx=0.4, rely=0.5)


    def create_canvas(self):
        sns.set_context('notebook')
        sns.set_style('white')
        self.fig = plt.Figure(dpi=72, figsize=(24,16))
        self.ax1 = self.fig.add_subplot(311)
        self.ax2 = self.fig.add_subplot(312)
        self.ax3 = self.fig.add_subplot(313)
        self.ax1.get_shared_x_axes().join(self.ax1, self.ax2, self.ax3)
        self.ax2.get_shared_x_axes().join(self.ax1, self.ax2, self.ax3)
        self.ax3.get_shared_x_axes().join(self.ax1, self.ax2, self.ax3)
        self.fig.subplots_adjust(hspace = 0.3)
        plt.close()
        canvas = tkagg.FigureCanvasTkAgg(self.fig , master=self.frm_canvas)
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
        self.ax1.autoscale_view()
        self.ax2.autoscale_view()
        self.ax3.autoscale_view()
        ax1_ylim = self.ax1.get_ylim()
        ax2_ylim = self.ax2.get_ylim()
        ax3_ylim = self.ax3.get_ylim()
        ax1_xlim = self.ax1.get_xlim()
        ax2_xlim = self.ax2.get_xlim()
        ax3_xlim = self.ax3.get_xlim()
        self.ax1.set_ylim([ax1_ylim[0], 1.3*ax1_ylim[1]])
        self.ax2.set_ylim([ax2_ylim[0], 1.3*ax2_ylim[1]])
        self.ax3.set_ylim([ax3_ylim[0], 1.3*ax3_ylim[1]])
        # set titles
        self.ax1.set_title(f"{plot_data[0]['kstnm']}.{plot_data[0]['kcmpnm']}")
        self.ax2.set_title(f"{plot_data[1]['kstnm']}.{plot_data[1]['kcmpnm']}")
        self.ax3.set_title(f"{plot_data[2]['kstnm']}.{plot_data[2]['kcmpnm']}")
        self.ax3.set_xlabel("Time (s)")

        color_selected = "#f00"
        color_not_selected = '#888'

        # update plot_data[3] and plot_data[4]
        p_phase_names = list(plot_data[3].keys())
        s_phase_names = list(plot_data[4].keys())
        num_p_phases = len(p_phase_names)
        num_s_phases = len(s_phase_names)

        p_index_start = self.get_select_status_index(self.plot_data_index)
        p_index_end = p_index_start + len(p_phase_names)
        s_index_start = p_index_end
        s_index_end = s_index_start + len(s_phase_names)
        select_status = self.current_select_status[p_index_start:s_index_end]

        i = 0
        for p_phase in plot_data[3].keys():
            plot_data[3][p_phase][1] = select_status[i]
            i += 1
        for s_phase in plot_data[4].keys():
            plot_data[4][s_phase][1] = select_status[i]
            i += 1


        
        # plot event origin
        color = color_not_selected
        self.ax1.plot([plot_data[0]['o'], plot_data[0]['o']], ax1_ylim, color=color, linestyle='dotted', linewidth=2)
        self.ax2.plot([plot_data[1]['o'], plot_data[1]['o']], ax2_ylim, color=color, linestyle='dotted', linewidth=2)
        self.ax3.plot([plot_data[2]['o'], plot_data[2]['o']], ax3_ylim, color=color, linestyle='dotted', linewidth=2)
        bbox_props = dict(facecolor='white', alpha=0.5)
        self.ax1.text(plot_data[0]['o'], ax1_ylim[1]*1.2, 'O', fontsize=12, color=color,
        verticalalignment='top',horizontalalignment='center', bbox=bbox_props, clip_on=True)
        self.ax2.text(plot_data[1]['o'], ax2_ylim[1]*1.2, 'O', fontsize=12, color=color,
        verticalalignment='top',horizontalalignment='center', bbox=bbox_props, clip_on=True)
        self.ax3.text(plot_data[2]['o'], ax3_ylim[1]*1.2, 'O', fontsize=12, color=color,
        verticalalignment='top',horizontalalignment='center', bbox=bbox_props, clip_on=True)

        # plot P arrivals
        select_status_index_start = self.get_select_status_index(self.plot_data_index)
        for iP, p_phase_name in enumerate(list(plot_data[3].keys())):
            p_phase_time = plot_data[3][p_phase_name][0]
            p_phase_selected = self.current_select_status[select_status_index_start + iP]
            if p_phase_selected:
                color = color_selected
            else:
                color = color_not_selected
            self.ax1.plot([p_phase_time, p_phase_time], ax1_ylim, color=color, linestyle='dashed', linewidth=2)
            self.ax2.plot([p_phase_time, p_phase_time], ax2_ylim, color=color, linestyle='dashed', linewidth=2)
            self.ax3.plot([p_phase_time, p_phase_time], ax3_ylim, color=color, linestyle='dashed', linewidth=2)
            self.ax1.text(p_phase_time, ax1_ylim[1]*1.2, p_phase_name, fontsize=12, color=color,
            verticalalignment='top',horizontalalignment='center', bbox=bbox_props, clip_on=True)
            self.ax2.text(p_phase_time, ax2_ylim[1]*1.2, p_phase_name, fontsize=12, color=color,
            verticalalignment='top',horizontalalignment='center', bbox=bbox_props, clip_on=True)
            self.ax3.text(p_phase_time, ax3_ylim[1]*1.2, p_phase_name, fontsize=12, color=color,
            verticalalignment='top',horizontalalignment='center', bbox=bbox_props, clip_on=True)

        # plot S arrivals
        select_status_index_start = self.get_select_status_index(self.plot_data_index) + len(list(plot_data[3].keys()))
        for iS, s_phase_name in enumerate(list(plot_data[4].keys())):
            s_phase_time = plot_data[4][s_phase_name][0]
            s_phase_selected = self.current_select_status[select_status_index_start + iS]
            if s_phase_selected:
                color = color_selected
            else:
                color = color_not_selected
            self.ax1.plot([s_phase_time, s_phase_time], ax1_ylim, color=color, linestyle='dashed', linewidth=2)
            self.ax2.plot([s_phase_time, s_phase_time], ax2_ylim, color=color, linestyle='dashed', linewidth=2)
            self.ax3.plot([s_phase_time, s_phase_time], ax3_ylim, color=color, linestyle='dashed', linewidth=2)
            self.ax1.text(s_phase_time, ax1_ylim[1]*1.2, s_phase_name, fontsize=12, color=color,
            verticalalignment='top',horizontalalignment='center', bbox=bbox_props, clip_on=True)
            self.ax2.text(s_phase_time, ax2_ylim[1]*1.2, s_phase_name, fontsize=12, color=color,
            verticalalignment='top',horizontalalignment='center', bbox=bbox_props, clip_on=True)
            self.ax3.text(s_phase_time, ax3_ylim[1]*1.2, s_phase_name, fontsize=12, color=color,
            verticalalignment='top',horizontalalignment='center', bbox=bbox_props, clip_on=True)

        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        self.canvas_toolbar.update()
        plt.close()


    def show_duplication_warning(self):
        duplicates = self.find_duplicates()
        duplicates = '\n'.join(duplicates)
        title = "Data duplication!"
        message = f"These sac files are ignored:\n\n{duplicates}"
        tkinter.messagebox.showinfo(title=title, message=message, parent=self.master)


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
                duplicates.append(f"  {os.path.basename(sacfile)}")
        return duplicates


    def get_plot_datalist(self):
        plot_datalist = []
        for event in self.sws_dataset.keys():
            for station in self.sws_dataset[event].keys():
                plot_data = []
                for channel in ['N','E','Z']:
                    sacfile_key = list(self.sws_dataset[event][station][channel].keys())[0]
                    plot_data.append(self.sws_dataset[event][station][channel][sacfile_key])
                plot_data.append(self.sws_dataset[event][station]['P'])
                plot_data.append(self.sws_dataset[event][station]['S'])
                plot_datalist.append(plot_data)
        return plot_datalist


    def get_sws_dataset(self):
        sws_dataset = {}
        # find uniq list of events
        events_uniq = []
        for key in sorted(self.sacfiles_info.keys()):
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
        del_stations = []
        for event in sws_dataset.keys():
            for station in sws_dataset[event].keys():
                del_station = False
                for channel in ['N','E','Z']:
                    if channel not in sws_dataset[event][station].keys() or len(sws_dataset[event][station][channel].keys()) == 0:
                        del_station = True
                del_stations.append(del_station)

        i = 0
        del_events = []
        events = list(sws_dataset.keys())
        for event in events:
            stations = list(sws_dataset[event].keys())
            for station in stations:
                if del_stations[i]:
                    del sws_dataset[event][station]
                i += 1
            if len(list(sws_dataset[event].keys())):
                del_events.append(False)
            else:
                del_events.append(True)

        i = 0
        for event in events:
            if del_events[i]:
                del sws_dataset[event]
            i += 1

        # calculate arrival times for P and S
        from obspy.taup import TauPyModel
        model = TauPyModel(model=self.refmodel)
        for event in sws_dataset.keys():
            for station in sws_dataset[event].keys():
                sacfile_key = list(sws_dataset[event][station]['Z'].keys())[0]
                # P arrivals
                ptt = model.get_travel_times(
                    source_depth_in_km=sws_dataset[event][station]['Z'][sacfile_key]['evdp'],
                    distance_in_degree=sws_dataset[event][station]['Z'][sacfile_key]['gcarc'],
                    phase_list=["ttp"]
                )
                arrivals_p = {}
                for i in range(len(ptt)):
                    cmp1 = self.sacfiles_info[list(sws_dataset[event][station]['N'].keys())[0]]['kcmpnm']
                    cmp2 = self.sacfiles_info[list(sws_dataset[event][station]['E'].keys())[0]]['kcmpnm']
                    cmp3 = self.sacfiles_info[list(sws_dataset[event][station]['Z'].keys())[0]]['kcmpnm']
                    fname1 = f"{os.path.basename(event)}_{station}_{ptt[i].name}.{cmp1}"
                    fname2 = f"{os.path.basename(event)}_{station}_{ptt[i].name}.{cmp2}"
                    fname3 = f"{os.path.basename(event)}_{station}_{ptt[i].name}.{cmp3}"
                    fname1 = os.path.join(event, fname1)
                    fname2 = os.path.join(event, fname2)
                    fname3 = os.path.join(event, fname3)
                    if os.path.isfile(fname1) and os.path.isfile(fname2) and os.path.isfile(fname3):
                        arrivals_p[f"{ptt[i].name}"] = [float(ptt[i].time), 1]
                    else:
                        arrivals_p[f"{ptt[i].name}"] = [float(ptt[i].time), 0]
                # sort by value:
                sorted_arrivals_p = sorted(arrivals_p.items(), key=operator.itemgetter(1))
                arrivals_p = {}
                for (key, val) in sorted_arrivals_p:
                    arrivals_p[key] = val


                # S arrivals
                stt = model.get_travel_times(
                    source_depth_in_km=sws_dataset[event][station]['Z'][sacfile_key]['evdp'],
                    distance_in_degree=sws_dataset[event][station]['Z'][sacfile_key]['gcarc'],
                    phase_list=["tts", "SKKS", "PKS"]
                )
                arrivals_s = {}
                for i in range(len(stt)):
                    cmp1 = self.sacfiles_info[list(sws_dataset[event][station]['N'].keys())[0]]['kcmpnm']
                    cmp2 = self.sacfiles_info[list(sws_dataset[event][station]['E'].keys())[0]]['kcmpnm']
                    cmp3 = self.sacfiles_info[list(sws_dataset[event][station]['Z'].keys())[0]]['kcmpnm']
                    fname1 = f"{os.path.basename(event)}_{station}_{stt[i].name}.{cmp1}"
                    fname2 = f"{os.path.basename(event)}_{station}_{stt[i].name}.{cmp2}"
                    fname3 = f"{os.path.basename(event)}_{station}_{stt[i].name}.{cmp3}"
                    fname1 = os.path.join(event, fname1)
                    fname2 = os.path.join(event, fname2)
                    fname3 = os.path.join(event, fname3)
                    if os.path.isfile(fname1) and os.path.isfile(fname2) and os.path.isfile(fname3):
                        arrivals_s[f"{stt[i].name}"] = [float(stt[i].time), 1]
                    else:
                        arrivals_s[f"{stt[i].name}"] = [float(stt[i].time), 0]
                # sort by value:
                sorted_arrivals_s = sorted(arrivals_s.items(), key=operator.itemgetter(1))
                arrivals_s = {}
                for (key, val) in sorted_arrivals_s:
                    arrivals_s[key] = val

                # append to sws dataset dictionary
                sws_dataset[event][station]['P'] = arrivals_p
                sws_dataset[event][station]['S'] = arrivals_s

        return sws_dataset

    

    def apply_update_dataset(self, event=None):
        if self.current_select_status == self.old_select_status:
            return
        self.lbl_statusbar["text"] = "Updating SWS dataset ..."
        i = 0 
        for event in self.sws_dataset.keys():
            for station in self.sws_dataset[event].keys():
                src1 = list(self.sws_dataset[event][station]['N'].keys())[0]
                src2 = list(self.sws_dataset[event][station]['E'].keys())[0]
                src3 = list(self.sws_dataset[event][station]['Z'].keys())[0]
                src1_split = os.path.splitext(src1)
                src2_split = os.path.splitext(src2)
                src3_split = os.path.splitext(src3)
                for p_phase in self.sws_dataset[event][station]['P'].keys():
                    dst1 = f"{src1_split[0]}_{p_phase}{src1_split[1]}"
                    dst2 = f"{src2_split[0]}_{p_phase}{src2_split[1]}"
                    dst3 = f"{src3_split[0]}_{p_phase}{src3_split[1]}"
                    if self.current_select_status[i] == 1:
                        # self.plot_datalist[self.plot_data_index][3][p_phase][1] = 1
                        shutil.copyfile(src1, dst1)
                        shutil.copyfile(src2, dst2)
                        shutil.copyfile(src3, dst3)
                    else:
                        # self.plot_datalist[self.plot_data_index][3][p_phase][1] = 0
                        if os.path.isfile(dst1):
                            os.remove(dst1)
                        if os.path.isfile(dst2):
                            os.remove(dst2)
                        if os.path.isfile(dst3):
                            os.remove(dst3)
                    i += 1
                for s_phase in self.sws_dataset[event][station]['S'].keys():
                    dst1 = f"{src1_split[0]}_{s_phase}{src1_split[1]}"
                    dst2 = f"{src2_split[0]}_{s_phase}{src2_split[1]}"
                    dst3 = f"{src3_split[0]}_{s_phase}{src3_split[1]}"
                    if self.current_select_status[i] == 1:
                        # self.plot_datalist[self.plot_data_index][4][s_phase][1] = 1
                        shutil.copyfile(src1, dst1)
                        shutil.copyfile(src2, dst2)
                        shutil.copyfile(src3, dst3)
                    else:
                        # self.plot_datalist[self.plot_data_index][4][s_phase][1] = 0
                        if os.path.isfile(dst1):
                            os.remove(dst1)
                        if os.path.isfile(dst2):
                            os.remove(dst2)
                        if os.path.isfile(dst3):
                            os.remove(dst3)
                    i += 1

        self.btn_update.config(state='disabled')
        self.file_menu.entryconfig("Update datasets", state="disabled")
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.lbl_statusbar["text"] = f"SWS dataset was last updated at {current_time}"


    def exit_program(self, event=None):
        self.master.destroy()


def run_sws_dataset_app(sacfiles, refmodel='iasp91', SAC='auto', headonly=False):
    print("Read sac files headers ...")
    sacfiles_info = sacproc.get_sacfiles_info(sacfiles, read_headers=True, read_data=True)
    root = tk.Tk()
    app = SWS_Dataset_App(sacfiles_info, master=root, refmodel=refmodel, SAC=SAC, headonly=headonly)
    app.mainloop()


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        print("Error! Must enter <sacfiles> as sys.argv[1:]!")
        exit(1)
    run_sws_dataset_app(sys.argv[1:])


