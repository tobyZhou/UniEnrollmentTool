# -*- coding: utf-8 -*-

import os
import sys
import pickle
import hashlib
import shutil
import time
from datetime import date
import Tkinter as Tk
import ttk
from xpinyin import Pinyin

Login_Title = "登录"
Key_In_Password = "输入密码: "
New_Password = "输入密码: "
Confirm_Password = "确认密码: "
Non_Match = "密码不一致，请重新输入"
Empty_Password = "密码不能为空"
Wrong_Password = "密码错误"
Confirm = "确认"
Cancel = "取消"
Add_New_University = "添加学校"
Search_Keyword = "搜索关键词"
Class_Science = "理科"
Class_Art = "文科"
Type_All = "全选"
Type_985 = "985工程"
Type_211 = "211工程"
Type_Leading_Uni = "一流大学"
Type_Leading_Sub = "一流学科"
Type_Others = "其他"
Refresh = "刷新"
Export = "导出文件"
Uni_Name = "大学"
Uni_Code = "代码"
Uni_Rank = "排名"
Uni_Types = "类别"
Uni_Details = "详情"
Uni_Plans = "招生计划"
Table_Header = ["序号", "排名", "大学", "代码", "类别"]
Table_Header_Size = [30, 40, 130, 40, 155, 45, 45, 60, 45, 45, 60, 45, 45, 60, 45, 45, 60]
Table_Pre_Batch = "提前批"
Table_First_Batch = "第一批"
Table_Accumulate = "累计"
Table_Details = "详情"
Detailed_String_Format = """                                                                                    
{}  (代码 - {}) \n
排名: {}\n
类别: {}\n
详情: {} \n\n
招生计划:
"""
Plan_Format = "{}年： 理科提前批{}人，第一批{}人； 文科提前批{}人，第一批{}人\n"
Plan_Note = "计划格式：每一行为这一年的计划。 年份，理科提前批和第一批人数，文科提前批和第一批人数用空格隔开。" \
            "\n例如：2018 10 20 5 9"

Default_Data_Dir = "default"
Custom_Data_Dir = "custom/data"
Custom_PW = "custom/pw.pickle"

Class_Science_Index = 0
Class_Art_Index = 1


class LoginPopUp(Tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        Tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.withdraw()
        print "Login Process"

        self.login_popup = Tk.Toplevel()
        self.login_popup.wm_title(Login_Title)
        self.login_popup.geometry("300x200")
        self.login_popup.attributes('-topmost', 'true')  # show at top lvl
        self.login_popup.grab_set()                      # disable other windows
        self.login_popup.protocol("WM_DELETE_WINDOW", self.on_closing)  # quit app on click "X"

        # Decide whether first time using pw file
        self.pw_log = os.path.join(os.getcwd(), Custom_PW)
        if os.path.isfile(self.pw_log):
            print "pw found"
            self.first_time = 0
            self.frame_pw = Tk.Frame(self.login_popup)
            self.frame_warning = Tk.Frame(self.login_popup)
            self.frame_buttons = Tk.Frame(self.login_popup)
            self.frame_pw.pack(pady=(30, 15))
            self.frame_warning.pack()
            self.frame_buttons.pack(pady=5)

            self.pw_text = Tk.Label(self.frame_pw, text=Key_In_Password)
            self.pw_input = Tk.Entry(self.frame_pw)
            self.pw_text.pack(side="left", padx=10)
            self.pw_input.pack(side="left", padx=10)

            self.warning_str = Tk.StringVar()
            self.warning = Tk.Label(self.frame_warning, fg='red', font='Helvetica 10 bold',
                                    textvariable=self.warning_str)
            self.warning.pack()

            self.submit_button = Tk.Button(self.frame_buttons, text=Confirm, command=self.pw_login)
            self.cancel_button = Tk.Button(self.frame_buttons, text=Cancel, command=self.on_closing)
            self.submit_button.pack(side="left", padx=10)
            self.cancel_button.pack(side="left", padx=10)

        else:
            print "pw not found"
            self.first_time = 1
            self.frame_new_pw = Tk.Frame(self.login_popup)
            self.frame_confirm_pw = Tk.Frame(self.login_popup)
            self.frame_buttons = Tk.Frame(self.login_popup)
            self.frame_warning = Tk.Frame(self.login_popup)
            self.frame_new_pw.pack(pady=(30, 15))
            self.frame_confirm_pw.pack(pady=(15, 20))
            self.frame_warning.pack()
            self.frame_buttons.pack(pady=5)

            self.new_pw_text = Tk.Label(self.frame_new_pw, text=New_Password)
            self.new_pw_input = Tk.Entry(self.frame_new_pw)
            self.new_pw_text.pack(side="left", padx=10)
            self.new_pw_input.pack(side="left", padx=10)

            self.confirm_pw_text = Tk.Label(self.frame_confirm_pw, text=Confirm_Password)
            self.confirm_pw_input = Tk.Entry(self.frame_confirm_pw)
            self.confirm_pw_text.pack(side="left", padx=10)
            self.confirm_pw_input.pack(side="left", padx=10)

            self.warning_str = Tk.StringVar()
            self.warning = Tk.Label(self.frame_warning, fg='red', font='Helvetica 10 bold',
                                    textvariable=self.warning_str)
            self.warning.pack()

            self.submit_button = Tk.Button(self.frame_buttons, width=10, text=Confirm, command=self.create_pw)
            self.cancel_button = Tk.Button(self.frame_buttons, width=10, text=Cancel, command=self.on_closing)
            self.submit_button.pack(side="left", padx=10)
            self.cancel_button.pack(side="left", padx=10)
        print "Pop up login windows"

    def create_pw(self):
        print "check and save password"
        new_pw = self.new_pw_input.get().strip()
        confirm_pw = self.confirm_pw_input.get().strip()

        if (not new_pw) or (not confirm_pw):
            print "empty password"
            self.warning_str.set(Empty_Password)
        elif new_pw != confirm_pw:
            print "not match"
            self.warning_str.set(Non_Match)
        else:
            print "create and log new password"
            # Save password
            if not os.path.exists(os.path.dirname(self.pw_log)):
                os.makedirs(os.path.dirname(self.pw_log))
            md5 = hashlib.md5(new_pw)
            with open(self.pw_log, 'wb') as f:
                pickle.dump({"pwmm": md5.digest()}, f, protocol=pickle.HIGHEST_PROTOCOL)

            # Copy default to custom if not exist
            custom_dir = os.path.join(os.getcwd(), Custom_Data_Dir)
            if os.path.exists(custom_dir) and os.listdir(custom_dir):
                print "Folder exists. Skip copy data set"
            else:
                if not os.path.exists(custom_dir):
                    os.mkdir(custom_dir)
                default_dir = os.path.join(os.getcwd(), Default_Data_Dir)
                for f in os.listdir(default_dir):
                    shutil.copyfile(os.path.join(default_dir, f), os.path.join(custom_dir, f))

            # Close popup
            self.login_popup.grab_release()
            self.login_popup.destroy()
            self.parent.deiconify()

    def pw_login(self):
        print "check log in password"

        pw = self.pw_input.get().strip()

        if not pw:
            print "Empty login password"
            self.warning_str.set(Empty_Password)
        else:
            with open(self.pw_log, 'rb') as f:
                saved_dic = pickle.load(f)
                saved_pw = saved_dic["pwmm"]
                md5 = hashlib.md5(pw)
                if saved_pw == md5.digest():
                    print "login password correct"
                    self.login_popup.grab_release()
                    self.login_popup.destroy()
                    self.parent.deiconify()
                else:
                    print "login password wrong"
                    self.warning_str.set(Wrong_Password)

    def on_closing(self):
        print "close popup"
        self.login_popup.destroy()
        self.parent.destroy()
        sys.exit(0)


class UniEditPopUp(Tk.Frame):
    def __init__(self, parent, uni_list, idx, *args, **kwargs):
        Tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.uni_list = uni_list
        if len(uni_list) == idx:
            # this is a new uni obj
            self.university = University()
            self.new_university = 1
        else:
            self.university = uni_list[idx]
            self.new_university = 0

        self.edit_popup = Tk.Toplevel()
        self.edit_popup.wm_title(self.university.name)
        self.edit_popup.geometry("700x650")
        self.edit_popup.attributes('-topmost', 'true')  # show at top lvl
        self.edit_popup.grab_set()                      # disable other windows

        self.frame = Tk.Frame(self.edit_popup)
        self.frame.pack(padx=40, pady=35)

        self.frame_name = Tk.Frame(self.frame)
        self.frame_name.pack(side=Tk.TOP, fill=Tk.X, pady=5)
        self.label_name = Tk.Label(self.frame_name, text=Uni_Name)
        self.label_name.pack(side=Tk.LEFT)
        self.label_name.setvar()
        self.entry_name = Tk.Entry(self.frame_name, width=50)
        self.entry_name.insert(Tk.END, self.university.name)
        self.entry_name.pack(side=Tk.LEFT, padx=15)

        self.frame_code = Tk.Frame(self.frame)
        self.frame_code.pack(side=Tk.TOP, fill=Tk.X, pady=5)
        self.label_code = Tk.Label(self.frame_code, text=Uni_Code)
        self.label_code.pack(side=Tk.LEFT)
        self.entry_code = Tk.Entry(self.frame_code, width=50)
        self.entry_code.insert(Tk.END, self.university.code)
        self.entry_code.pack(side=Tk.LEFT, padx=15)

        self.frame_rank = Tk.Frame(self.frame)
        self.frame_rank.pack(side=Tk.TOP, fill=Tk.X, pady=5)
        self.label_rank = Tk.Label(self.frame_rank, text=Uni_Rank)
        self.label_rank.pack(side=Tk.LEFT)
        self.entry_rank = Tk.Entry(self.frame_rank, width=50)
        self.entry_rank.insert(Tk.END, self.university.rank)
        self.entry_rank.pack(side=Tk.LEFT, padx=15)

        self.frame_types = Tk.Frame(self.frame)
        self.frame_types.pack(side=Tk.TOP, fill=Tk.X, pady=2)
        self.type_985_value = Tk.IntVar()
        self.type_985_value.set(self.university.type_985)
        self.type_985 = Tk.Checkbutton(self.frame_types, text=Type_985, variable=self.type_985_value)
        self.type_985.pack(side=Tk.LEFT, padx=10, pady=(3, 10))
        self.type_211_value = Tk.IntVar()
        self.type_211_value.set(self.university.type_211)
        self.type_211 = Tk.Checkbutton(self.frame_types, text=Type_211, variable=self.type_211_value)
        self.type_211.pack(side=Tk.LEFT, padx=10, pady=(3, 10))
        self.type_lead_uni_value = Tk.IntVar()
        self.type_lead_uni_value.set(self.university.type_lead_uni)
        self.type_lead_uni = Tk.Checkbutton(self.frame_types, text=Type_Leading_Uni, variable=self.type_lead_uni_value)
        self.type_lead_uni.pack(side=Tk.LEFT, padx=10, pady=(3, 10))
        self.type_lead_sub_value = Tk.IntVar()
        self.type_lead_sub_value.set(self.university.type_lead_sub)
        self.type_lead_sub = Tk.Checkbutton(self.frame_types, text=Type_Leading_Sub, variable=self.type_lead_sub_value)
        self.type_lead_sub.pack(side=Tk.LEFT, padx=10, pady=(3, 10))

        self.frame_details = Tk.Frame(self.frame)
        self.frame_details.pack(side=Tk.TOP, fill=Tk.X, pady=5)
        self.label_details = Tk.Label(self.frame_details, text=Uni_Details)
        self.label_details.pack(side=Tk.LEFT)
        self.entry_details = Tk.Text(self.frame_details, height=10, width=70)
        self.entry_details.insert(Tk.END, self.university.details)
        self.entry_details.pack(side=Tk.LEFT, padx=23)

        self.frame_plans = Tk.Frame(self.frame)
        self.frame_plans.pack(side=Tk.TOP, fill=Tk.X, pady=10)
        self.label_plans = Tk.Label(self.frame_plans, text=Uni_Plans)
        self.label_plans.pack(side=Tk.LEFT)
        self.entry_plans = Tk.Text(self.frame_plans, height=10, width=70)
        self.entry_plans.insert(Tk.END, self.university.get_plan_string())
        self.entry_plans.pack(side=Tk.LEFT)
        self.frame_plan_note = Tk.Frame(self.frame)
        self.frame_plan_note.pack(side=Tk.TOP, fill=Tk.X)
        self.label_plan_note = Tk.Label(self.frame_plan_note, text=Plan_Note)
        self.label_plan_note.pack()

        self.frame_buttons = Tk.Frame(self.frame)
        self.frame_buttons.pack(side=Tk.TOP, fill=Tk.X, padx=60, pady=10)
        self.button_submit = Tk.Button(self.frame_buttons, text=Confirm, command=self.confirm_edit, width=20)
        self.button_submit.pack(side=Tk.LEFT)
        self.button_cancel = Tk.Button(self.frame_buttons, text=Cancel, command=self.cancel_edit, width=20)
        self.button_cancel.pack(side=Tk.LEFT, padx=100)

    def confirm_edit(self):
        '''print "submit edit"
        print "name: ", self.entry_name.get()
        print "code: ", self.entry_code.get()
        print self.entry_rank.get()
        print self.type_985_value.get()
        print self.type_211_value.get()
        print self.type_lead_uni_value.get()
        print self.type_lead_sub_value.get()
        print self.entry_details.get(1.0, Tk.END).strip()
        print self.entry_plans.get(1.0, Tk.END).strip()'''

        self.university.name = self.entry_name.get().strip()
        self.university.code = self.entry_code.get().strip()
        self.university.rank = self.entry_rank.get().strip()
        '''if self.entry_rank.get().isdigit():
            self.university.rank = int(self.entry_rank.get())
        else:
            self.university.rank = float(self.entry_rank.get())'''
        self.university.type_985 = self.type_985_value.get()
        self.university.type_211 = self.type_211_value.get()
        self.university.type_lead_uni = self.type_lead_uni_value.get()
        self.university.type_lead_sub = self.type_lead_sub_value.get()
        self.university.details = self.entry_details.get(1.0, Tk.END).strip()
        self.university.update_plan(self.entry_plans.get(1.0, Tk.END).strip())

        self.university.write_to_dist(os.path.join(os.getcwd(), Custom_Data_Dir))

        if self.new_university:
            self.parent.add_new_university(self.university)
        else:
            self.parent.update_uni_order_after_edit()

        self.edit_popup.grab_release()
        self.edit_popup.destroy()

    def cancel_edit(self):
        self.edit_popup.grab_release()
        self.edit_popup.destroy()


class UniSystem(Tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        Tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.login_object = LoginPopUp(self.parent)

        # gui = uni_page + display_page
        self.uni_page = Tk.Frame(self.parent, bd=2, relief=Tk.RIDGE)
        self.uni_page.pack(side=Tk.LEFT, fill=Tk.Y, ipadx=20, ipady=20)
        self.display_page = Tk.Frame(self.parent)
        self.display_page.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True, padx=10, pady=20)

        # uni_page = uni_content + management page
        self.uni_content = Tk.Frame(self.uni_page)
        self.uni_content.pack(side=Tk.TOP, fill=Tk.Y, expand=True, pady=(20, 0))
        self.uni_management = Tk.Frame(self.uni_page)
        self.uni_management.pack(side=Tk.BOTTOM)

        # uni_content page
        self.uni_canvas = Tk.Canvas(self.uni_content)
        self.uni_canvas.config(width=130)
        self.uni_canvas.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True)
        self.uni_scrollbar = Tk.Scrollbar(self.uni_content, command=self.uni_canvas.yview)
        self.uni_scrollbar.pack(side=Tk.LEFT, fill=Tk.Y)
        self.uni_canvas.configure(yscrollcommand=self.uni_scrollbar.set)

        self.uni_canvas.bind('<Configure>', self._on_frame_configure)
        self.uni_canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.uni_canvas.bind('<Leave>', self._unbound_to_mousewheel)

        self.uni_list_frame = Tk.Frame(self.uni_canvas)
        self.uni_list_frame.bind("<Configure>", self._reset_scrollregion)
        self.uni_canvas.create_window((0, 0), window=self.uni_list_frame, anchor='nw')
        # add sth
        self.university_list = []   # sorted at start, remain the same after edit and add new
        self.university_list_sorted = []  # always sorted in rank
        self.candidates = []
        self.load_universities()

        # Uni_management page
        self.uni_add_button = Tk.Button(self.uni_management, text=Add_New_University, command=self.popup_new_uni_window)
        self.uni_add_button.pack(pady=20)

        # -------------------------------------
        # display page = search + filters + table
        self.search_frame = Tk.Frame(self.display_page)
        self.search_frame.pack(side=Tk.TOP, fill=Tk.X)
        self.display_filters = Tk.Frame(self.display_page)
        self.display_filters.pack(side=Tk.TOP, fill=Tk.X)
        self.display_table = Tk.Frame(self.display_page, bd=1, relief=Tk.RIDGE)
        self.display_table.pack(side=Tk.TOP, fill=Tk.BOTH, expand=True)

        # search frame
        self.search_label = Tk.Label(self.search_frame, text=Search_Keyword)
        self.search_label.pack(side=Tk.LEFT, padx=(25, 0))
        self.search_entry = Tk.Entry(self.search_frame)
        self.search_entry.pack(side=Tk.LEFT, fill=Tk.X, expand=True, padx=(20, 40))

        # display filters: two class and 4 types + refresh button
        self.filter_content = Tk.Frame(self.display_filters)
        self.filter_content.pack(side=Tk.LEFT, fill=Tk.X, expand=True)
        self.filter_button_frame = Tk.Frame(self.display_filters)
        self.filter_button_frame.pack(side=Tk.LEFT)

        self.filter_class = Tk.Frame(self.filter_content)
        self.filter_class.pack(side=Tk.TOP, fill=Tk.X)
        self.filter_types = Tk.Frame(self.filter_content)
        self.filter_types.pack(side=Tk.TOP, fill=Tk.X)

        self.filter_refresh_button = Tk.Button(self.filter_button_frame, text=Refresh, width=10,
                                               command=self.refresh_table)
        self.filter_refresh_button.pack(side=Tk.LEFT)
        self.export_button = Tk.Button(self.filter_button_frame, text=Export, width=10, command=self.export_csv)
        self.export_button.pack(side=Tk.LEFT, padx=30)

        # filter class
        self.class_value = Tk.IntVar()
        self.class_value.set(Class_Science_Index)  # default is science
        self.science_button = Tk.Radiobutton(self.filter_class, text=Class_Science, variable=self.class_value,
                                             value=Class_Science_Index, command=self.update_class)
        self.science_button.pack(side=Tk.LEFT, padx=(20, 10), pady=(10, 2))
        self.art_button = Tk.Radiobutton(self.filter_class, text=Class_Art, variable=self.class_value,
                                         value=Class_Art_Index, command=self.update_class)
        self.art_button.pack(side=Tk.LEFT, padx=10, pady=(10, 2))

        # filter types
        # type all
        self.type_all_value = Tk.IntVar()
        self.type_all_value.set(1)
        self.type_all = Tk.Checkbutton(self.filter_types, text=Type_All, variable=self.type_all_value,
                                       command=self.update_all_types)
        self.type_all.pack(side=Tk.LEFT, padx=(20, 10), pady=(3, 10))
        # type 985
        self.type_985_value = Tk.IntVar()
        self.type_985_value.set(1)
        self.type_985 = Tk.Checkbutton(self.filter_types, text=Type_985, variable=self.type_985_value,
                                       command=self.update_individual_type)
        self.type_985.pack(side=Tk.LEFT, padx=10, pady=(3, 10))
        # type 211
        self.type_211_value = Tk.IntVar()
        self.type_211_value.set(1)
        self.type_211 = Tk.Checkbutton(self.filter_types, text=Type_211, variable=self.type_211_value,
                                       command=self.update_individual_type)
        self.type_211.pack(side=Tk.LEFT, padx=10, pady=(3, 10))
        # type lead uni
        self.type_lead_uni_value = Tk.IntVar()
        self.type_lead_uni_value.set(1)
        self.type_lead_uni = Tk.Checkbutton(self.filter_types, text=Type_Leading_Uni,
                                            variable=self.type_lead_uni_value, command=self.update_individual_type)
        self.type_lead_uni.pack(side=Tk.LEFT, padx=10, pady=(3, 10))
        # type lead sub
        self.type_lead_sub_value = Tk.IntVar()
        self.type_lead_sub_value.set(1)
        self.type_lead_sub = Tk.Checkbutton(self.filter_types, text=Type_Leading_Sub,
                                            variable=self.type_lead_sub_value, command=self.update_individual_type)
        self.type_lead_sub.pack(side=Tk.LEFT, padx=10, pady=(3, 10))
        # type others
        self.type_others_value = Tk.IntVar()
        self.type_others_value.set(1)
        self.type_others_checkButton = Tk.Checkbutton(self.filter_types, text=Type_Others,
                                                      variable=self.type_others_value,
                                                      command=self.update_individual_type)
        self.type_others_checkButton.pack(side=Tk.LEFT, padx=10, pady=(2, 10))

        # display table
        self.current_year = date.today().year
        self.headers = [Table_Header[0], Table_Header[1], Table_Header[2], Table_Header[3], Table_Header[4],
                        Table_Pre_Batch, Table_First_Batch, str(self.current_year-3) + Table_Accumulate,
                        Table_Pre_Batch, Table_First_Batch, str(self.current_year-2) + Table_Accumulate,
                        Table_Pre_Batch, Table_First_Batch, str(self.current_year-1) + Table_Accumulate,
                        Table_Pre_Batch, Table_First_Batch, str(self.current_year) + Table_Accumulate]
        self.tree = ttk.Treeview(columns=range(len(self.headers)), show="headings")
        self.tree_vsb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        self.tree_hsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.tree_vsb.set,
                            xscrollcommand=self.tree_hsb.set)

        self.tree.grid(column=0, row=0, sticky='nsew', in_=self.display_table)
        self.tree_vsb.grid(column=1, row=0, sticky='ns', in_=self.display_table)
        self.tree_hsb.grid(column=0, row=1, sticky='ew', in_=self.display_table)

        self.display_table.grid_columnconfigure(0, weight=1)
        self.display_table.grid_rowconfigure(0, weight=1)

        self.tree.bind('<Enter>', self._bound_to_mousewheel_table)
        self.tree.bind('<Leave>', self._unbound_to_mousewheel_table)
        self.tree.bind('<Double-1>', self.popup_details)

        self.fill_table()

    def _on_frame_configure(self, event):
        self.uni_canvas.configure(scrollregion=self.uni_canvas.bbox("all"))

    def _bound_to_mousewheel(self, event):
        self.uni_canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

    def _unbound_to_mousewheel(self, event):
        self.uni_canvas.unbind_all("<MouseWheel>")

    def _on_mouse_wheel(self, event):
        self.uni_canvas.yview_scroll(-1*(event.delta/120), "units")

    def _reset_scrollregion(self, event):
        self.uni_canvas.configure(scrollregion=self.uni_canvas.bbox("all"))

    def _on_frame_configure_table(self, event):
        self.tree.configure(scrollregion=self.tree)

    def _bound_to_mousewheel_table(self, event):
        self.tree.bind_all("<MouseWheel>", self._on_mouse_wheel_table)

    def _unbound_to_mousewheel_table(self, event):
        self.tree.unbind_all("<MouseWheel>")

    def _on_mouse_wheel_table(self, event):
        self.tree.yview_scroll(-1*(event.delta/120), "units")

    def load_universities(self):
        print "load data"

        # set data path. (custom if not default)
        custom_path = os.path.join(os.getcwd(), Custom_Data_Dir)
        if os.path.exists(custom_path) and os.listdir(custom_path):
            log_dir = custom_path
        else:
            log_dir = os.path.join(os.getcwd(), Default_Data_Dir)

        # load uni info
        for f in os.listdir(log_dir):
            uni_obj = University()
            uni_obj.load_from_log(os.path.join(log_dir, f))
            self.university_list.append(uni_obj)
        self.university_list.sort(key=lambda x: x.pinyin)  # Sort University !!
        self.university_list_sorted = [uni for uni in self.university_list]

        # create uni buttons
        for i, uni in enumerate(self.university_list):
            button = Tk.Button(self.uni_list_frame, text=uni.name,
                               command=lambda idx=i: self.popup_edit_uni_window(idx))
            button.pack(fill=Tk.X)

    def popup_new_uni_window(self):
        print "add new uni"
        UniEditPopUp(self, self.university_list, len(self.university_list))

    def add_new_university(self, uni):
        print "back add button now"
        self.university_list.append(uni)
        self.university_list_sorted = sorted(self.university_list, key=lambda x: (len(x.rank), x.rank))

        button = Tk.Button(self.uni_list_frame, text=uni.name,
                           command=lambda idx=uni.id: self.popup_edit_uni_window(idx))
        button.pack(fill=Tk.X)

    def popup_edit_uni_window(self, idx):
        print "Edit uni id: ", idx
        UniEditPopUp(self, self.university_list, idx)

    def update_uni_order_after_edit(self):
        # reset list with new ranks if changed
        self.university_list_sorted.sort(key=lambda x: (len(x.rank), x.rank))

    def update_class(self):
        print "Update class choice"
        print self.class_value.get()

    def update_all_types(self):
        print "Reset types based on all"
        print "all: ", self.type_all_value.get()

        if self.type_all_value.get() == 1:
            self.type_985_value.set(1)
            self.type_211_value.set(1)
            self.type_lead_uni_value.set(1)
            self.type_lead_sub_value.set(1)
            self.type_others_value.set(1)
        elif self.type_all_value.get() == 0:
            self.type_985_value.set(0)
            self.type_211_value.set(0)
            self.type_lead_uni_value.set(0)
            self.type_lead_sub_value.set(0)
            self.type_others_value.set(0)
        else:
            print "Invalid all type"

    def update_individual_type(self):
        print "Update type choices"
        print "985:{}  211:{}  LeadUni:{}  LeadSub:{}  Others:{}".format(self.type_985_value.get(),
                                                                         self.type_211_value.get(),
                                                                         self.type_lead_uni_value.get(),
                                                                         self.type_lead_sub_value.get(),
                                                                         self.type_others_value.get())
        if (self.type_985_value.get() == 1 and self.type_211_value.get() == 1
                and self.type_lead_uni_value.get() == 1 and self.type_lead_sub_value.get() == 1
                and self.type_others_value.get() == 1):
            self.type_all_value.set(1)
        else:
            self.type_all_value.set(0)

    def fill_table(self):
        # Update accumulated plans
        yr_current = date.today().year
        class_choice = self.class_value.get()
        yr_accu = [0, 0]  # one for pre-batch, one for first-batch
        yr_last_1_accu = [0, 0]
        yr_last_2_accu = [0, 0]
        yr_last_3_accu = [0, 0]
        for uni in self.university_list_sorted:
            if yr_current in uni.plans:
                yr_accu[0] += uni.plans[yr_current][0 + 2*class_choice]
                yr_accu[1] += uni.plans[yr_current][1 + 2*class_choice]
                uni.update_accumulated_plan(yr_current, class_choice, yr_accu[0]+yr_accu[1])
            if (yr_current-1) in uni.plans:
                yr_last_1_accu[0] += uni.plans[yr_current-1][0 + 2*class_choice]
                yr_last_1_accu[1] += uni.plans[yr_current-1][1 + 2*class_choice]
                uni.update_accumulated_plan(yr_current-1, class_choice, yr_last_1_accu[0]+yr_last_1_accu[1])
            if (yr_current-2) in uni.plans:
                yr_last_2_accu[0] += uni.plans[yr_current-2][0 + 2*class_choice]
                yr_last_2_accu[1] += uni.plans[yr_current-2][1 + 2*class_choice]
                uni.update_accumulated_plan(yr_current-2, class_choice, yr_last_2_accu[0]+yr_last_2_accu[1])
            if (yr_current-3) in uni.plans:
                yr_last_3_accu[0] += uni.plans[yr_current-3][0 + 2*class_choice]
                yr_last_3_accu[1] += uni.plans[yr_current-3][1 + 2*class_choice]
                uni.update_accumulated_plan(yr_current-3, class_choice, yr_last_3_accu[0]+yr_last_3_accu[1])

        # Filter types for display
        self.candidates = []
        keyword = self.search_entry.get().encode('utf-8')
        for uni in self.university_list_sorted:
            if ((self.type_985_value.get() and uni.type_985)
                    or (self.type_211_value.get() and uni.type_211)
                    or (self.type_lead_uni_value.get() and uni.type_lead_uni)
                    or (self.type_lead_sub_value.get() and uni.type_lead_sub)
                    or (self.type_others_value.get() and uni.type_985 == 0 and uni.type_211 == 0 and
                        uni.type_lead_uni == 0 and uni.type_lead_sub == 0)
                    or self.type_all_value.get()):
                if keyword:
                    if keyword in uni.name.encode('utf-8'):
                        self.candidates.append(uni)
                else:
                    self.candidates.append(uni)
        self.candidates.sort(key=lambda x: (len(x.rank), x.rank))

        # Display table content
        print "update display based on class and types"
        for i, h in enumerate(self.headers):
            self.tree.heading(i, text=h)
            self.tree.column(i, width=Table_Header_Size[i])
            #self.tree.column(i, width=tkFont.Font().measure(h))

        for can_id, candidate in enumerate(self.candidates):
            row_info = [can_id+1]
            row_info.extend(candidate.get_info_list(class_choice))
            self.tree.insert("", "end", value=row_info)
            '''for ix, val in enumerate(row_info):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(ix, width=None) < col_w:
                    self.tree.column(ix, width=col_w)'''

    def refresh_table(self):
        print " clear table first "
        self.tree.delete(*self.tree.get_children())

        self.fill_table()

    def popup_details(self, event):
        print self.tree.item(self.tree.focus())
        uni_name = self.tree.item(self.tree.focus())['values'][2]
        print uni_name

        for candidate in self.candidates:
            if candidate.name == uni_name:
                details_popup = Tk.Toplevel()
                details_popup.wm_title(candidate.name)
                details_popup.geometry("500x500")

                self.details_canvas = Tk.Canvas(details_popup)
                self.details_canvas.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True)
                details_scrollbar = Tk.Scrollbar(details_popup, command=self.details_canvas.yview)
                details_scrollbar.pack(side=Tk.LEFT, fill=Tk.Y)
                self.details_canvas.config(yscrollcommand=details_scrollbar.set)
                self.details_canvas.bind("<Configure>", self.detail_popup_scrollbar)

                details_frame = Tk.Frame(self.details_canvas)
                details_frame.bind("<Configure>", self.detail_popup_scrollbar)
                self.details_canvas.create_window((0, 0), window=details_frame, anchor='nw')
                details_text = Tk.Label(details_frame, width=70, wraplength=400, justify=Tk.LEFT,
                                        text=candidate.get_info_str_details(), anchor='w')
                details_text.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True, anchor='w', pady=25, padx=40)

    def detail_popup_scrollbar(self, event):
        self.details_canvas.configure(scrollregion=self.details_canvas.bbox("all"))

    def export_csv(self):
        print "write candidates to csv"
        output_str = ""
        for r in xrange(len(self.candidates) + 1):
            if r == 0:
                output_str += ",".join(Table_Header)
                for i in xrange(self.current_year - 3, self.current_year + 1):
                    output_str += ",{}".format(i)
                    output_str += ",{}".format(str(i) + Table_Accumulate)
            else:
                row_info = self.candidates[r - 1].get_info_list(self.class_value.get())
                new_row_info = []
                for v in row_info:
                    if isinstance(v, unicode):
                        new_row_info.append(v.encode('utf-8'))
                    else:
                        new_row_info.append(str(v))
                output_str += ",".join(new_row_info)
            output_str += "\n"

        log_name = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime()) + ".csv"
        with open(log_name, "w") as f:
            f.write(output_str)


class University:

    def __init__(self, name="", code="", rank="10000", type_985=0, type_211=0, type_lead_uni=0, type_lead_sub=0,
                 details="", plans={}, pinyin=""):
        self.name = name   # string
        self.code = code   # string
        self.rank = rank   # string. default is 10000.
        self.type_985 = type_985    # int
        self.type_211 = type_211    # int
        self.type_lead_uni = type_lead_uni    # int
        self.type_lead_sub = type_lead_sub    # int
        self.details = details    # string (with new line char)
        self.plans = plans   # dic{yr:[science-pre, science_1st, art-pre, art-1st]} all int
        self.accumulated_plans = {}
        self.pinyin = ""  # no need to save to log.

    def get_plan_string(self):
        values = [[key, value[0], value[1], value[2], value[3]] for key, value in self.plans.iteritems()]
        values.sort(key=lambda x: x[0])

        plan_string = ""
        for v in values:
            plan_string += "{} {} {} {} {}\n".format(v[0], v[1], v[2], v[3], v[4])

        return plan_string

    # For both add and modify
    def update_plan(self, plan_string):
        print "update plan"
        self.plans = {}
        if plan_string:
            for line in plan_string.split("\n"):
                values = line.split()
                self.plans[int(values[0])] = [int(values[1]), int(values[2]), int(values[3]), int(values[4])]

    def update_accumulated_plan(self, year, class_choice, number):
        print "update accumulate plan"
        if year in self.accumulated_plans:
            self.accumulated_plans[year][class_choice] = number
        else:
            if class_choice == Class_Science_Index:
                self.accumulated_plans[year] = [number, 0]
            else:
                self.accumulated_plans[year] = [0, number]

    def write_to_dist(self, log_folder):
        print "Write to log"
        output = {}
        output["name"] = self.name
        output["code"] = self.code
        output["rank"] = self.rank
        output["type_985"] = self.type_985
        output["type_211"] = self.type_211
        output["type_lead_uni"] = self.type_lead_uni
        output["type_lead_sub"] = self.type_lead_sub
        output["details"] = self.details
        output["plans"] = self.plans

        log_file = os.path.join(log_folder.decode('GB2312').encode('utf-8'),
                                "{}.pickle".format(self.name.encode('utf-8')))
        log_file = unicode(log_file, "utf8")
        with open(log_file, 'wb') as f:
            pickle.dump(output, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_from_log(self, log_file):
        with open(log_file, 'rb') as f:
            saved_dic = pickle.load(f)
            self.name = saved_dic["name"]
            self.code = saved_dic["code"]
            self.rank = str(saved_dic["rank"])
            self.type_985 = saved_dic["type_985"]
            self.type_211 = saved_dic["type_211"]
            self.type_lead_uni = saved_dic["type_lead_uni"]
            self.type_lead_sub = saved_dic["type_lead_sub"]
            self.details = saved_dic["details"]
            self.plans = saved_dic["plans"]
            p = Pinyin()
            self.pinyin = p.get_pinyin(self.name).encode("utf-8") # make a string for sorting

    def get_info_list(self, class_type):
        type_str = self.get_type_string()

        yr_current = date.today().year
        yr_before = yr_current - 1
        yr_before_last = yr_current - 2
        yr_before_last_last = yr_current - 3

        yr_current_value = [0, 0]
        yr_before_value = [0, 0]
        yr_before_last_value = [0, 0]
        yr_before_last_last_value = [0, 0]
        if yr_current in self.plans:
            for i in xrange(2):
                yr_current_value[i] = self.plans[yr_current][i + 2*class_type]
        if yr_before in self.plans:
            for i in xrange(2):
                yr_before_value[i] = self.plans[yr_before][i + 2*class_type]
        if yr_before_last in self.plans:
            for i in xrange(2):
                yr_before_last_value[i] = self.plans[yr_before_last][i + 2*class_type]
        if yr_before_last_last in self.plans:
            for i in xrange(2):
                yr_before_last_last_value[i] = self.plans[yr_before_last_last][i + 2*class_type]

        yr_current_value_accum = 0
        yr_before_value_accum = 0
        yr_before_last_value_accum = 0
        yr_before_last_last_value_accum = 0
        if yr_current in self.accumulated_plans:
            yr_current_value_accum = self.accumulated_plans[yr_current][class_type]
        if yr_before in self.accumulated_plans:
            yr_before_value_accum = self.accumulated_plans[yr_before][class_type]
        if yr_before_last in self.accumulated_plans:
            yr_before_last_value_accum = self.accumulated_plans[yr_before_last][class_type]
        if yr_before_last_last in self.accumulated_plans:
            yr_before_last_last_value_accum = self.accumulated_plans[yr_before_last_last][class_type]

        info = [self.rank, self.name, self.code, type_str,
                yr_before_last_last_value[0], yr_before_last_last_value[1], yr_before_last_last_value_accum,
                yr_before_last_value[0], yr_before_last_value[1], yr_before_last_value_accum,
                yr_before_value[0], yr_before_value[1], yr_before_value_accum,
                yr_current_value[0], yr_current_value[1], yr_current_value_accum]

        return info

    def get_info_str_details(self):
        type_str = self.get_type_string()

        info_str = Detailed_String_Format.format(self.name.encode('utf-8'), self.code, self.rank, type_str,
                                                 self.details.encode('utf-8'))

        values = [[key, value[0], value[1], value[2], value[3]] for key, value in self.plans.iteritems()]
        values.sort(key=lambda x: x[0])
        for v in values:
            info_str += Plan_Format.format(v[0], v[1], v[2], v[3], v[4])

        return info_str

    def get_type_string(self):
        elements = []
        if self.type_985:
            elements.append(Type_985)
        if self.type_211:
            elements.append(Type_211)
        if self.type_lead_uni:
            elements.append(Type_Leading_Uni)
        if self.type_lead_sub and not self.type_lead_uni:
            elements.append(Type_Leading_Sub)
        return ";".join(elements)


def create_default_uni_files():
    print "create default files"
    names_log = './files/2018-63.csv'
    with open(names_log, 'r') as f:
        lines = [n.strip() for n in f.readlines()]

    u_list = []
    for line in lines:
        values = line.split(',')
        print values
        uni = University(rank=values[0].strip(), name=values[1].strip().decode('utf-8'), code=values[2].strip())
        u_list.append(uni)

    # append those not in 2018-63
    all_log = './files/University-names'
    with open(all_log, 'r') as f:
        names = [n.strip().decode('utf-8') for n in f.readlines()]

    for name in names:
        # check whether alrdy exist.
        exist = 0
        for alr_u in u_list:
            if alr_u.name == name:
                exist = 1
                break
        if not exist:
            uni = University(name=name)
            u_list.append(uni)
    print u_list[1].name
    print names[0]
    print u_list[1].name == names[0]
    print len(u_list)

    # write out
    output_dir = os.path.join(os.getcwd(), Default_Data_Dir)
    for uni in u_list:
        uni.write_to_dist(output_dir)

    sys.exit(0)


if __name__ == "__main__":
    # create_default_uni_files()
    root = Tk.Tk()
    root.geometry("1240x650")
    root.title("University System")
    UniSystem(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
