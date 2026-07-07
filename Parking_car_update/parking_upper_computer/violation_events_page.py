import os
import random
import sys
from datetime import datetime, timedelta


def ensure_tk_runtime():
    """Point tkinter at the bundled Tcl/Tk runtime when Python misses it."""
    base_dir = os.path.dirname(sys.executable)
    tcl_root = os.path.join(base_dir, "tcl")
    tcl_library = os.path.join(tcl_root, "tcl8.6")
    tk_library = os.path.join(tcl_root, "tk8.6")

    if os.path.isdir(tcl_library) and not os.environ.get("TCL_LIBRARY"):
        os.environ["TCL_LIBRARY"] = tcl_library
    if os.path.isdir(tk_library) and not os.environ.get("TK_LIBRARY"):
        os.environ["TK_LIBRARY"] = tk_library


ensure_tk_runtime()

import tkinter as tk
from tkinter import ttk


APP_BG = "#0f172a"
PANEL_BG = "#111827"
CARD_BG = "#1f2937"
CARD_ALT_BG = "#172033"
TEXT_PRIMARY = "#f3f4f6"
TEXT_SECONDARY = "#9ca3af"
ACCENT_BLUE = "#38bdf8"
ACCENT_GREEN = "#22c55e"
ACCENT_ORANGE = "#f59e0b"
ACCENT_RED = "#ef4444"
ACCENT_PURPLE = "#8b5cf6"
LINE_COLOR = "#243041"

PLATE_PREFIXES = ["粤B", "鲁A", "沪C", "川A", "苏E", "浙A", "鄂A", "湘A", "闽C", "豫A"]
PLATE_LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ"
PLATE_ALNUM = PLATE_LETTERS + "0123456789"
PLATE_DIGITS = "0123456789"
VIOLATION_TYPES = ["错停", "乱停", "消防通道占用", "充电位占用", "禁停区占用"]
AREAS = ["A区", "B区", "C区", "D区"]
STATUS_CHOICES = ["未处理", "已通知", "已处理"]
SEVERITY_CHOICES = ["高", "中", "低"]
OWNER_NAMES = ["张伟", "王芳", "李娜", "刘洋", "陈杰", "赵敏", "黄磊", "周婷", "吴凯", "徐晨", "孙磊", "罗丹"]
COLORS = ["白色", "黑色", "银色", "灰色", "蓝色", "红色"]
VEHICLE_TYPES = ["轿车", "SUV", "新能源车", "商务车"]
CAPTURE_DEVICES = ["巡检小车-01", "巡检小车-02", "固定摄像头-东入口", "固定摄像头-充电区"]
REMARKS = [
    "请尽快联系车主。",
    "重复违规车辆，建议重点关注。",
    "现场影响通行，优先处理。",
    "需复核抓拍信息后再通知。",
    "建议电话提醒并记录回访。",
]


def random_fuel_plate():
    prefix = random.choice(PLATE_PREFIXES)
    first_letter = random.choice(PLATE_LETTERS)
    serial = "".join(random.choice(PLATE_ALNUM) for _ in range(4))
    return f"{prefix}{first_letter}{serial}"


def random_new_energy_plate(pure_electric=None):
    prefix = random.choice(PLATE_PREFIXES)
    if pure_electric is None:
        pure_electric = random.random() < 0.7

    energy_code = "D" if pure_electric else "F"
    serial_head = random.choice(PLATE_ALNUM)
    serial_tail = "".join(random.choice(PLATE_DIGITS) for _ in range(4))
    return f"{prefix}{energy_code}{serial_head}{serial_tail}"


def random_plate(is_new_energy=None, pure_electric=None):
    if is_new_energy is None:
        is_new_energy = random.random() < 0.35

    if is_new_energy:
        return random_new_energy_plate(pure_electric=pure_electric)
    return random_fuel_plate()


def random_phone():
    prefixes = ["130", "135", "138", "150", "156", "178", "186", "189"]
    return f"{random.choice(prefixes)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"


def random_area_slot():
    return f"{random.choice(AREAS)}-{random.randint(1, 28):03d}"


def severity_for_type(violation_type):
    if violation_type in {"消防通道占用", "禁停区占用"}:
        return "高"
    return random.choice(["中", "低"])


def build_event_records(alert_event=None):
    now = datetime.now()
    records = []
    if alert_event is None:
        alert_event = {
            "plate": "\u5dddB 968CT",
            "violation_type": "\u538b\u7ebf\u505c\u8f66",
            "area": "B\u533a-018",
            "status": "\u672a\u5904\u7406",
        }

    records.append(
        {
            "event_id": f"E{now.strftime('%Y%m%d')}001",
            "plate": alert_event["plate"],
            "owner": "\u8d75\u6587\u51ef",
            "phone": random_phone(),
            "type": alert_event["violation_type"],
            "time": (now - timedelta(minutes=3)).strftime("%Y-%m-%d %H:%M"),
            "area": alert_event["area"],
            "status": alert_event.get("status", "\u672a\u5904\u7406"),
            "severity": "\u9ad8",
            "vehicle_type": "\u8f7f\u8f66",
            "color": "\u6df1\u7070",
            "remark": "\u68c0\u6d4b\u5230\u8f66\u8f86\u538b\u7ebf\u505c\u8f66\uff0c\u5df2\u89e6\u53d1\u5b9e\u65f6\u544a\u8b66\u3002",
            "history_count": 2,
            "capture_device": "\u5317\u4fa7\u5de1\u68c0\u6444\u50cf\u5934",
            "duration": "\u6301\u7eed 7 \u5206\u949f",
            "last_notice": "\u672a\u901a\u77e5",
        }
    )

    for index in range(21):
        violation_type = random.choice(VIOLATION_TYPES)
        status = random.choices(STATUS_CHOICES, weights=[5, 3, 2], k=1)[0]
        event_time = now - timedelta(minutes=random.randint(5, 360))
        last_notice = event_time + timedelta(minutes=random.randint(5, 30))
        history_count = random.randint(0, 4)
        vehicle_type = random.choice(VEHICLE_TYPES)
        is_new_energy = vehicle_type == "新能源车"
        record = {
            "event_id": f"E{now.strftime('%Y%m%d')}{index + 2:03d}",
            "plate": random_plate(is_new_energy=is_new_energy),
            "owner": random.choice(OWNER_NAMES),
            "phone": random_phone(),
            "type": violation_type,
            "time": event_time.strftime("%Y-%m-%d %H:%M"),
            "area": random_area_slot(),
            "status": status,
            "severity": severity_for_type(violation_type),
            "vehicle_type": vehicle_type,
            "color": random.choice(COLORS),
            "remark": random.choice(REMARKS),
            "history_count": history_count,
            "capture_device": random.choice(CAPTURE_DEVICES),
            "duration": f"\u6301\u7eed {random.randint(6, 48)} \u5206\u949f",
            "last_notice": last_notice.strftime("%H:%M") if status != "未处理" else "未通知",
        }
        records.append(record)

    records.sort(key=lambda item: (item["status"] != "未处理", item["time"]))
    return records


class ViolationEventsPage:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("停车场巡检小车上位机 - 违规事件")
        self.root.geometry("1540x940")
        self.root.minsize(1280, 780)
        self.root.configure(bg=APP_BG)


        self.alert_event = {
            "plate": "\u5dddB 968CT",
            "violation_type": "\u538b\u7ebf\u505c\u8f66",
            "area": "B\u533a-018",
            "status": "\u672a\u5904\u7406",
        }
        self.alert_banner = None
        self.alert_message_var = tk.StringVar()
        self.alert_animation_after = None
        self.alert_dismiss_after = None
        self.alert_flash_after = None
        self.alert_flash_state = False
        self.status_filter = tk.StringVar(value="全部")
        self.type_filter = tk.StringVar(value="全部")
        self.severity_filter = tk.StringVar(value="全部")
        self.keyword_var = tk.StringVar()
        self.info_var = tk.StringVar()

        self.records = []
        self.filtered_records = []
        self.selected_record = None

        self.detail_vars = {
            "event_id": tk.StringVar(value="-"),
            "plate": tk.StringVar(value="-"),
            "owner": tk.StringVar(value="-"),
            "phone": tk.StringVar(value="-"),
            "type": tk.StringVar(value="-"),
            "time": tk.StringVar(value="-"),
            "area": tk.StringVar(value="-"),
            "status": tk.StringVar(value="-"),
            "severity": tk.StringVar(value="-"),
            "vehicle_type": tk.StringVar(value="-"),
            "color": tk.StringVar(value="-"),
            "remark": tk.StringVar(value="-"),
            "history_count": tk.StringVar(value="-"),
            "capture_device": tk.StringVar(value="-"),
            "duration": tk.StringVar(value="-"),
            "last_notice": tk.StringVar(value="-"),
        }

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._configure_styles()
        self._reload_random_data(initial=True)
        self._build_layout()
        self.root.after(500, self._show_violation_alert)
        self._refresh_chips()
        self._apply_filters()

    def _configure_styles(self):
        self.style.configure(
            "Events.Treeview",
            background=CARD_BG,
            fieldbackground=CARD_BG,
            foreground=TEXT_PRIMARY,
            rowheight=36,
            borderwidth=0,
            relief="flat",
            font=("Microsoft YaHei UI", 10),
        )
        self.style.configure(
            "Events.Treeview.Heading",
            background=CARD_ALT_BG,
            foreground=TEXT_SECONDARY,
            relief="flat",
            borderwidth=0,
            font=("Microsoft YaHei UI", 10, "bold"),
        )
        self.style.map(
            "Events.Treeview",
            background=[("selected", "#233044")],
            foreground=[("selected", TEXT_PRIMARY)],
        )

    def _build_layout(self):
        container = self._create_page_container()
        container.grid_columnconfigure(0, weight=5)
        container.grid_columnconfigure(1, weight=3)
        container.grid_rowconfigure(2, weight=1)

        self._build_top_bar(container)
        self._build_filter_bar(container)
        self._build_main_section(container)

    def _build_top_bar(self, parent):
        top_bar = tk.Frame(parent, bg=APP_BG)
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        top_bar.grid_columnconfigure(0, weight=1)

        left = tk.Frame(top_bar, bg=APP_BG)
        left.grid(row=0, column=0, sticky="w")
        tk.Label(left, text="违规事件", bg=APP_BG, fg=TEXT_PRIMARY, font=("Microsoft YaHei UI", 22, "bold")).pack(anchor="w")
        tk.Label(left, text="事件筛选、详情查看与处理记录", bg=APP_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 10)).pack(anchor="w", pady=(6, 0))

        right = tk.Frame(top_bar, bg=APP_BG)
        right.grid(row=0, column=1, sticky="e")
        self.total_chip = self._build_chip(right, "事件总数 0", ACCENT_ORANGE)
        self.total_chip.pack(side="left", padx=(0, 12))
        self.pending_chip = self._build_chip(right, "未处理 0", ACCENT_RED)
        self.pending_chip.pack(side="left", padx=(0, 12))
        self.high_chip = self._build_chip(right, "高优先级 0", ACCENT_PURPLE)
        self.high_chip.pack(side="left")

    def _build_chip(self, parent, text, color):
        chip = tk.Frame(parent, bg=PANEL_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
        dot = tk.Canvas(chip, width=12, height=12, bg=PANEL_BG, highlightthickness=0)
        dot.create_oval(2, 2, 10, 10, fill=color, outline=color)
        dot.pack(side="left", padx=(14, 8), pady=12)
        label = tk.Label(chip, text=text, bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Microsoft YaHei UI", 10, "bold"))
        label.pack(side="left", padx=(0, 14))
        chip.label = label
        return chip

    def _set_chip_text(self, chip, text):
        chip.label.config(text=text)

    def _bind_mousewheel(self, canvas, widget):
        def _on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(-int(event.delta / 120), "units")
            elif getattr(event, "num", None) == 4:
                canvas.yview_scroll(-1, "units")
            elif getattr(event, "num", None) == 5:
                canvas.yview_scroll(1, "units")

        def _activate(_event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)

        def _deactivate(_event):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        widget.bind("<Enter>", _activate, add="+")
        widget.bind("<Leave>", _deactivate, add="+")
        canvas.bind("<Enter>", _activate, add="+")
        canvas.bind("<Leave>", _deactivate, add="+")

    def _create_page_container(self):
        outer = tk.Frame(self.root, bg=APP_BG)
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=APP_BG, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=APP_BG, padx=24, pady=20)

        content_window = canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        content.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda event: self._update_canvas_window(canvas, content_window, content, event.width, event.height),
        )

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._bind_mousewheel(canvas, content)
        return content

    def _update_canvas_window(self, canvas, content_window, content, width, height):
        canvas.itemconfigure(content_window, width=width, height=max(height, content.winfo_reqheight()))

    def _build_filter_bar(self, parent):
        filters = tk.Frame(parent, bg=PANEL_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
        filters.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        filters.grid_columnconfigure(7, weight=1)

        tk.Label(filters, text="状态", bg=PANEL_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 10)).grid(row=0, column=0, padx=(16, 8), pady=14)
        tk.OptionMenu(filters, self.status_filter, "全部", "全部", *STATUS_CHOICES, command=lambda _value: self._apply_filters()).grid(row=0, column=1, padx=(0, 12), pady=10)

        tk.Label(filters, text="违规类型", bg=PANEL_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 10)).grid(row=0, column=2, padx=(0, 8), pady=14)
        tk.OptionMenu(filters, self.type_filter, "全部", "全部", *VIOLATION_TYPES, command=lambda _value: self._apply_filters()).grid(row=0, column=3, padx=(0, 12), pady=10)

        tk.Label(filters, text="等级", bg=PANEL_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 10)).grid(row=0, column=4, padx=(0, 8), pady=14)
        tk.OptionMenu(filters, self.severity_filter, "全部", "全部", *SEVERITY_CHOICES, command=lambda _value: self._apply_filters()).grid(row=0, column=5, padx=(0, 12), pady=10)

        tk.Label(filters, text="车牌关键字", bg=PANEL_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 10)).grid(row=0, column=6, padx=(0, 8), pady=14)
        keyword_entry = tk.Entry(filters, textvariable=self.keyword_var, bg=CARD_ALT_BG, fg=TEXT_PRIMARY, relief="flat", insertbackground=TEXT_PRIMARY, width=18)
        keyword_entry.grid(row=0, column=7, sticky="w", padx=(0, 12), pady=12)
        keyword_entry.bind("<KeyRelease>", lambda _event: self._apply_filters())

        tk.Button(filters, text="重置筛选", command=self._reset_filters, bg=CARD_ALT_BG, fg=TEXT_PRIMARY, relief="flat", bd=0, padx=16, pady=8, font=("Microsoft YaHei UI", 9, "bold"), cursor="hand2").grid(row=0, column=8, padx=(0, 10), pady=10)
        tk.Button(filters, text="刷新数据", command=self._reload_and_refresh, bg=ACCENT_BLUE, fg="#0b1120", relief="flat", bd=0, padx=16, pady=8, font=("Microsoft YaHei UI", 9, "bold"), cursor="hand2").grid(row=0, column=9, padx=(0, 16), pady=10)

    def _build_main_section(self, parent):
        table_panel = tk.Frame(parent, bg=PANEL_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
        table_panel.grid(row=2, column=0, sticky="nsew", padx=(0, 10))
        table_panel.grid_rowconfigure(2, weight=1)
        table_panel.grid_columnconfigure(0, weight=1)

        detail_panel = tk.Frame(parent, bg=PANEL_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
        detail_panel.grid(row=2, column=1, sticky="nsew")

        self._build_table_panel(table_panel)
        self._build_detail_panel(detail_panel)

    def _build_table_panel(self, parent):
        tk.Label(parent, text="事件列表", bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Microsoft YaHei UI", 14, "bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 4))
        tk.Label(parent, textvariable=self.info_var, bg=PANEL_BG, fg=ACCENT_BLUE, font=("Microsoft YaHei UI", 9)).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 12))

        columns = ("event_id", "plate", "type", "time", "area", "status", "severity")
        table_frame = tk.Frame(parent, bg=PANEL_BG)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 16))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        table_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Events.Treeview",
            yscrollcommand=table_scrollbar.set,
        )
        table_scrollbar.config(command=self.tree.yview)
        self.tree.grid(row=0, column=0, sticky="nsew")
        table_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        headings = {
            "event_id": "事件编号",
            "plate": "车牌号",
            "type": "违规类型",
            "time": "发现时间",
            "area": "区域",
            "status": "处理状态",
            "severity": "等级",
        }
        widths = {
            "event_id": 140,
            "plate": 120,
            "type": 130,
            "time": 160,
            "area": 90,
            "status": 100,
            "severity": 70,
        }

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="center")

    def _build_detail_panel(self, parent):
        tk.Label(parent, text="事件详情", bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Microsoft YaHei UI", 14, "bold")).pack(anchor="w", padx=18, pady=(16, 4))
        tk.Label(parent, text="查看车牌、车主、违规说明和处理动作", bg=PANEL_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 9)).pack(anchor="w", padx=18, pady=(0, 12))

        detail_box = tk.Frame(parent, bg=PANEL_BG)
        detail_box.pack(fill="both", expand=True, padx=18, pady=(0, 12))

        detail_items = [
            ("事件编号", "event_id"),
            ("车牌号", "plate"),
            ("车主姓名", "owner"),
            ("联系电话", "phone"),
            ("违规类型", "type"),
            ("发现时间", "time"),
            ("区域位置", "area"),
            ("处理状态", "status"),
            ("告警等级", "severity"),
            ("车辆类型", "vehicle_type"),
            ("车辆颜色", "color"),
            ("抓拍来源", "capture_device"),
            ("占用时长", "duration"),
            ("最近通知", "last_notice"),
            ("历史违规", "history_count"),
            ("处理备注", "remark"),
        ]

        for label_text, key in detail_items:
            card = tk.Frame(detail_box, bg=CARD_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
            card.pack(fill="x", pady=5)
            tk.Label(card, text=label_text, bg=CARD_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 10), padx=14, pady=10).pack(anchor="w")
            value_label = tk.Label(
                card,
                textvariable=self.detail_vars[key],
                bg=CARD_BG,
                fg=TEXT_PRIMARY,
                font=("Microsoft YaHei UI", 11, "bold"),
                padx=14,
                anchor="w",
                justify="left",
                wraplength=420,
            )
            value_label.pack(fill="x", pady=(0, 10))

        action_bar = tk.Frame(parent, bg=PANEL_BG)
        action_bar.pack(fill="x", padx=18, pady=(0, 18))
        tk.Button(action_bar, text="标记为已处理", command=self._mark_processed, bg=ACCENT_GREEN, fg="#04130a", relief="flat", bd=0, padx=16, pady=8, font=("Microsoft YaHei UI", 9, "bold"), cursor="hand2").pack(side="left", padx=(0, 10))
        tk.Button(action_bar, text="模拟电话通知", command=self._mark_notified, bg=ACCENT_ORANGE, fg="#271504", relief="flat", bd=0, padx=16, pady=8, font=("Microsoft YaHei UI", 9, "bold"), cursor="hand2").pack(side="left", padx=(0, 10))
        tk.Button(action_bar, text="加入重点跟进", command=self._mark_follow_up, bg=ACCENT_PURPLE, fg="#140a26", relief="flat", bd=0, padx=16, pady=8, font=("Microsoft YaHei UI", 9, "bold"), cursor="hand2").pack(side="left")

    def _show_violation_alert(self):
        if self.alert_banner is not None:
            self.alert_banner.destroy()

        self.alert_message_var.set(
            f"\u8fdd\u505c\u63d0\u9192  {self.alert_event['plate']} \u672a\u6309\u8f66\u4f4d\u89c4\u8303\u505c\u8f66\uff0c\u5b58\u5728\u538b\u7ebf\u60c5\u51b5\uff0c\u8bf7\u53ca\u65f6\u5904\u7406"
        )

        banner = tk.Frame(
            self.root,
            bg="#7f1d1d",
            highlightbackground="#fca5a5",
            highlightthickness=1,
        )
        banner.place(relx=0.5, y=-120, anchor="n", width=760, height=92)
        banner.lift()

        left_bar = tk.Frame(banner, bg="#ef4444", width=8)
        left_bar.pack(side="left", fill="y")

        content = tk.Frame(banner, bg="#7f1d1d")
        content.pack(side="left", fill="both", expand=True, padx=20, pady=14)

        tk.Label(
            content,
            text="\u5b9e\u65f6\u8fdd\u89c4\u544a\u8b66",
            bg="#7f1d1d",
            fg="#fee2e2",
            font=("Microsoft YaHei UI", 13, "bold"),
        ).pack(anchor="w")
        tk.Label(
            content,
            textvariable=self.alert_message_var,
            bg="#7f1d1d",
            fg=TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 11),
            wraplength=660,
            justify="left",
        ).pack(anchor="w", pady=(8, 0))

        tk.Label(
            banner,
            text="\u6301\u7eed\u76d1\u6d4b\u4e2d",
            bg="#7f1d1d",
            fg="#fecaca",
            font=("Microsoft YaHei UI", 10, "bold"),
            padx=18,
        ).pack(side="right")

        self.alert_banner = banner
        self.alert_flash_state = False
        self._animate_alert_in(-120, 24, 18)
        self._flash_alert_banner()
        self._highlight_primary_event()
        self.alert_dismiss_after = self.root.after(6500, self._hide_violation_alert)

    def _animate_alert_in(self, current_y, target_y, steps_left):
        if self.alert_banner is None:
            return

        if steps_left <= 0:
            self.alert_banner.place_configure(y=target_y)
            self.alert_animation_after = None
            return

        next_y = current_y + (target_y - current_y) / steps_left
        self.alert_banner.place_configure(y=int(next_y))
        self.alert_animation_after = self.root.after(
            18,
            lambda: self._animate_alert_in(next_y, target_y, steps_left - 1),
        )

    def _flash_alert_banner(self):
        if self.alert_banner is None:
            return

        self.alert_flash_state = not self.alert_flash_state
        bg_color = "#991b1b" if self.alert_flash_state else "#7f1d1d"
        border_color = "#fca5a5" if self.alert_flash_state else "#fecaca"

        self.alert_banner.configure(bg=bg_color, highlightbackground=border_color)
        for widget in self.alert_banner.winfo_children():
            self._apply_alert_palette(widget, bg_color)

        self.alert_flash_after = self.root.after(320, self._flash_alert_banner)

    def _apply_alert_palette(self, widget, bg_color):
        if isinstance(widget, tk.Frame) and str(widget.cget("bg")) != "#ef4444":
            widget.configure(bg=bg_color)
        elif isinstance(widget, tk.Label):
            widget.configure(bg=bg_color)

        for child in widget.winfo_children():
            self._apply_alert_palette(child, bg_color)

    def _hide_violation_alert(self):
        if self.alert_animation_after is not None:
            self.root.after_cancel(self.alert_animation_after)
            self.alert_animation_after = None
        if self.alert_flash_after is not None:
            self.root.after_cancel(self.alert_flash_after)
            self.alert_flash_after = None
        if self.alert_dismiss_after is not None:
            self.root.after_cancel(self.alert_dismiss_after)
            self.alert_dismiss_after = None

        if self.alert_banner is not None:
            self.alert_banner.destroy()
            self.alert_banner = None

    def _highlight_primary_event(self):
        if not hasattr(self, "tree"):
            return

        alert_iid = None
        for record in self.filtered_records:
            if record["plate"] == self.alert_event["plate"]:
                alert_iid = record["event_id"]
                break

        if alert_iid and self.tree.exists(alert_iid):
            self.tree.selection_set(alert_iid)
            self.tree.focus(alert_iid)
            self.tree.see(alert_iid)
            for record in self.filtered_records:
                if record["event_id"] == alert_iid:
                    self._set_detail(record)
                    break

    def _refresh_chips(self):
        total = len(self.records)
        pending = sum(1 for item in self.records if item["status"] == "未处理")
        high = sum(1 for item in self.records if item["severity"] == "高")
        self._set_chip_text(self.total_chip, f"事件总数 {total}")
        self._set_chip_text(self.pending_chip, f"未处理 {pending}")
        self._set_chip_text(self.high_chip, f"高优先级 {high}")

    def _update_info_text(self):
        self.info_var.set(f"当前筛选结果 {len(self.filtered_records)} 条 / 总事件 {len(self.records)} 条")

    def _populate_table(self, records):
        self.tree.delete(*self.tree.get_children())
        for index, record in enumerate(records):
            row_tags = ["evenrow" if index % 2 == 0 else "oddrow"]
            if record["plate"] == self.alert_event["plate"]:
                row_tags.append("alertrow")
            self.tree.insert(
                "",
                "end",
                iid=record["event_id"],
                values=(record["event_id"], record["plate"], record["type"], record["time"], record["area"], record["status"], record["severity"]),
                tags=tuple(row_tags),
            )

        self.tree.tag_configure("evenrow", background=CARD_BG)
        self.tree.tag_configure("oddrow", background="#1b2432")
        self.tree.tag_configure("alertrow", background="#4c0519", foreground="#fee2e2")

        if records:
            self.tree.selection_set(records[0]["event_id"])
            self.tree.focus(records[0]["event_id"])
            self._set_detail(records[0])
            self._highlight_primary_event()
        else:
            self.selected_record = None
            for var in self.detail_vars.values():
                var.set("-")

    def _set_detail(self, record):
        self.selected_record = record
        for key, var in self.detail_vars.items():
            value = record.get(key, "")
            if key == "history_count":
                value = f"{value} 次"
            var.set(value)

    def _on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return

        event_id = selected[0]
        for record in self.filtered_records:
            if record["event_id"] == event_id:
                self._set_detail(record)
                break

    def _apply_filters(self):
        keyword = self.keyword_var.get().strip().upper()
        filtered = []

        for record in self.records:
            if self.status_filter.get() != "全部" and record["status"] != self.status_filter.get():
                continue
            if self.type_filter.get() != "全部" and record["type"] != self.type_filter.get():
                continue
            if self.severity_filter.get() != "全部" and record["severity"] != self.severity_filter.get():
                continue
            if keyword and keyword not in record["plate"].upper():
                continue
            filtered.append(record)

        self.filtered_records = filtered
        self._populate_table(filtered)
        self._update_info_text()

    def _reset_filters(self):
        self.status_filter.set("全部")
        self.type_filter.set("全部")
        self.severity_filter.set("全部")
        self.keyword_var.set("")
        self._apply_filters()

    def _mark_processed(self):
        if not self.selected_record:
            return
        self.selected_record["status"] = "已处理"
        self.selected_record["remark"] = "已标记为已处理，等待归档。"
        self.selected_record["last_notice"] = datetime.now().strftime("%H:%M")
        self._refresh_chips()
        self._apply_filters()

    def _mark_notified(self):
        if not self.selected_record:
            return
        self.selected_record["status"] = "已通知"
        self.selected_record["remark"] = "已模拟执行电话通知流程，等待车主驶离。"
        self.selected_record["last_notice"] = datetime.now().strftime("%H:%M")
        self._refresh_chips()
        self._apply_filters()

    def _mark_follow_up(self):
        if not self.selected_record:
            return
        self.selected_record["severity"] = "高"
        self.selected_record["remark"] = "已加入重点跟进列表，建议安排复检。"
        self._refresh_chips()
        self._apply_filters()

    def _reload_random_data(self, initial=False):
        self.records = build_event_records(self.alert_event)
        self.filtered_records = list(self.records)
        self.selected_record = self.records[0] if self.records else None
        if not initial:
            self._refresh_chips()

    def _reload_and_refresh(self):
        self._reload_random_data()
        self._refresh_chips()
        self._apply_filters()


def main():
    root = tk.Tk()
    ViolationEventsPage(root)
    root.mainloop()


if __name__ == "__main__":
    main()
