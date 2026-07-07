import os
import random
import subprocess
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
from tkinter import messagebox, ttk


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
TASK_CHOICES = ["巡检中", "待机", "返航中", "暂停巡检"]
NETWORK_CHOICES = ["Wi-Fi 良好", "Wi-Fi 一般", "4G 回传正常"]
SERIAL_CHOICES = ["正常", "正常，延迟 8ms", "正常，延迟 12ms"]
ZONE_TEXT = ["主通道", "北侧车道", "南侧车道", "充电区入口", "访客区入口"]
STATUS_CHOICES = ["未处理", "已通知", "已处理"]


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


def random_area_slot():
    return f"{random.choice(AREAS)}-{random.randint(1, 28):03d}"


def format_duration(total_seconds):
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def make_event_record(event_id, plate, violation_type, event_time, area, status):
    return {
        "event_id": event_id,
        "plate": plate,
        "violation_type": violation_type,
        "time": event_time,
        "area": area,
        "status": status,
    }


def build_dashboard_state(alert_event=None):
    now = datetime.now()
    owners_count = random.randint(368, 428)
    total_events = random.randint(9, 14)
    pending_events = random.randint(3, 5)
    high_priority = random.randint(0, min(2, pending_events))
    inspected_areas = random.sample(AREAS, k=random.randint(2, 4))
    task_name = random.choice([
        "停车场日常巡检",
        "重点区域复检",
        "午间高峰巡检",
    ])
    task_state = random.choices(TASK_CHOICES, weights=[6, 1, 1, 1], k=1)[0]
    heartbeat_sec = random.randint(1, 3)
    battery = random.randint(68, 92)
    abnormal_count = random.randint(0, 1)
    patrol_seconds = random.randint(5400, 12800)
    mileage_km = round(random.uniform(2.6, 5.8), 1)
    task_progress = random.randint(61, 88)
    current_area = f"{random.choice(AREAS)} {random.choice(ZONE_TEXT)}"
    network_status = random.choices(NETWORK_CHOICES, weights=[6, 2, 1], k=1)[0]
    serial_status = random.choices(SERIAL_CHOICES, weights=[6, 2, 1], k=1)[0]
    recent_new_events = random.randint(1, 2)

    if alert_event is None:
        alert_event = {
            "plate": random_plate(),
            "violation_type": random.choice(VIOLATION_TYPES),
            "area": random_area_slot(),
            "status": "未处理",
        }

    event_records = [
        make_event_record(
            f"P{now.strftime('%Y%m%d')}001",
            alert_event["plate"],
            alert_event["violation_type"],
            now - timedelta(seconds=random.randint(20, 80)),
            alert_event["area"],
            alert_event.get("status", "未处理"),
        )
    ]

    for index in range(1, 8):
        event_records.append(
            make_event_record(
                f"P{now.strftime('%Y%m%d')}{index + 1:03d}",
                random_plate(),
                random.choice(VIOLATION_TYPES),
                now - timedelta(minutes=random.randint(5 + index * 4, 12 + index * 10)),
                random_area_slot(),
                random.choices(STATUS_CHOICES, weights=[2, 3, 5], k=1)[0],
            )
        )

    system_logs = [
        {"time": now, "source": "系统", "message": "首页已加载，当前数据回传正常。"},
        {"time": now - timedelta(minutes=1), "source": "小车", "message": f"当前任务状态：{task_state}，状态同步正常。"},
        {"time": now - timedelta(minutes=2), "source": "事件", "message": f"检测到违规车辆：{alert_event['plate']}，位置 {alert_event['area']}。"},
        {"time": now - timedelta(minutes=4), "source": "数据库", "message": f"车主信息库读取成功，已同步 {owners_count} 条记录。"},
        {"time": now - timedelta(minutes=6), "source": "巡检", "message": f"当前已覆盖 {len(inspected_areas)} 个区域，巡检时长 {format_duration(patrol_seconds)}。"},
        {"time": now - timedelta(minutes=8), "source": "告警", "message": "当前存在待处理违规事件，请及时查看。"},
    ]

    return {
        "owners_count": owners_count,
        "total_events": total_events,
        "pending_events": pending_events,
        "handled_events": total_events - pending_events,
        "high_priority": high_priority,
        "online": True,
        "heartbeat_sec": heartbeat_sec,
        "battery": battery,
        "abnormal_count": abnormal_count,
        "patrol_seconds": patrol_seconds,
        "mileage_km": mileage_km,
        "task_progress": task_progress,
        "task_name": task_name,
        "task_state": task_state,
        "current_area": current_area,
        "network_status": network_status,
        "serial_status": serial_status,
        "inspected_areas": inspected_areas,
        "recent_new_events": recent_new_events,
        "event_records": event_records,
        "system_logs": system_logs,
        "next_event_index": 9,
        "tick_count": 0,
    }


def build_summary_data(state):
    recent_detail = (
        f"近10分钟新增 {state['recent_new_events']} 起"
        if state["recent_new_events"]
        else "近10分钟无新增"
    )
    return [
        {
            "title": "今日违规事件",
            "value": str(state["total_events"]),
            "detail": recent_detail,
            "accent": ACCENT_ORANGE,
        },
        {
            "title": "未处理事件",
            "value": str(state["pending_events"]),
            "detail": f"其中高优先级 {state['high_priority']} 起",
            "accent": ACCENT_RED,
        },
        {
            "title": "小车在线状态",
            "value": "在线" if state["online"] else "离线",
            "detail": f"最后心跳 {state['heartbeat_sec']} 秒前",
            "accent": ACCENT_GREEN if state["online"] else ACCENT_RED,
        },
        {
            "title": "车主信息总数",
            "value": str(state["owners_count"]),
            "detail": "车辆信息已同步",
            "accent": ACCENT_BLUE,
        },
    ]


def build_event_rows(state):
    return [
        (
            item["event_id"],
            item["plate"],
            item["violation_type"],
            item["time"].strftime("%Y-%m-%d %H:%M"),
            item["area"],
            item["status"],
        )
        for item in state["event_records"]
    ]


def build_robot_status(state):
    return [
        ("当前任务", state["task_name"]),
        ("任务状态", state["task_state"]),
        ("当前区域", state["current_area"]),
        ("电池电量", f"{state['battery']}%"),
        ("网络状态", state["network_status"]),
        ("串口状态", state["serial_status"]),
        ("异常计数", f"{state['abnormal_count']} 次"),
        ("今日里程", f"{state['mileage_km']:.1f} km"),
        ("本轮巡检", f"已完成 {state['task_progress']}%"),
    ]


def build_system_logs(state):
    return [
        (item["time"].strftime("%H:%M:%S"), item["source"], item["message"])
        for item in state["system_logs"]
    ]


def build_trend_data(state):
    return [
        ("已巡检区域", " / ".join(state["inspected_areas"])),
        ("累计巡检时长", format_duration(state["patrol_seconds"])),
        ("已处理事件", f"{state['handled_events']} 起"),
        ("高优先级事件", f"{state['high_priority']} 起"),
        ("当前数据状态", "实时回传正常"),
        ("重点关注", "违规事件、车辆查询、通知记录"),
    ]


def build_demo_data(alert_event=None):
    state = build_dashboard_state(alert_event)
    return (
        build_summary_data(state),
        build_event_rows(state),
        build_robot_status(state),
        build_system_logs(state),
        build_trend_data(state),
        state,
    )


def open_violation_events_page():
    target = os.path.join(os.path.dirname(__file__), "violation_events_page.py")
    if not os.path.exists(target):
        messagebox.showerror("打开失败", "未找到违规事件页脚本。")
        return

    try:
        subprocess.Popen([sys.executable, target])
    except OSError as exc:
        messagebox.showerror("打开失败", f"无法打开违规事件页：\n{exc}")


class HomePageApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("停车场巡检小车上位机 - 首页")
        self.root.geometry("1460x900")
        self.root.minsize(1180, 760)
        self.root.configure(bg=APP_BG)

        self.alert_event = {
            "plate": "川B 968CT",
            "violation_type": "压线停车",
            "area": "B区-018",
            "status": "未处理",
        }
        self.alert_banner = None
        self.alert_message_var = tk.StringVar()
        self.alert_animation_after = None
        self.alert_dismiss_after = None
        self.alert_flash_after = None
        self.alert_flash_state = False

        self.time_var = tk.StringVar()
        self.search_var = tk.StringVar(value="输入车牌号快速查询")

        self.summary_data = []
        self.event_rows = []
        self.robot_status = []
        self.system_logs = []
        self.trend_data = []
        self.dashboard_state = {}
        self.summary_card_widgets = []
        self.status_value_labels = {}
        self.log_item_widgets = []
        self.trend_value_labels = {}
        self.realtime_update_after = None

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._configure_styles()
        self._load_demo_data()
        self._build_layout()
        self.root.after(500, self._show_violation_alert)
        self._refresh_dashboard_view()
        self.root.after(2500, self._schedule_realtime_update)
        self._update_clock()

    def _configure_styles(self):
        self.style.configure(
            "Dashboard.Treeview",
            background=CARD_BG,
            fieldbackground=CARD_BG,
            foreground=TEXT_PRIMARY,
            rowheight=36,
            borderwidth=0,
            relief="flat",
            font=("Microsoft YaHei UI", 10),
        )
        self.style.configure(
            "Dashboard.Treeview.Heading",
            background=CARD_ALT_BG,
            foreground=TEXT_SECONDARY,
            relief="flat",
            borderwidth=0,
            font=("Microsoft YaHei UI", 10, "bold"),
        )
        self.style.map(
            "Dashboard.Treeview",
            background=[("selected", "#233044")],
            foreground=[("selected", TEXT_PRIMARY)],
        )

    def _load_demo_data(self):
        (
            self.summary_data,
            self.event_rows,
            self.robot_status,
            self.system_logs,
            self.trend_data,
            self.dashboard_state,
        ) = build_demo_data(self.alert_event)
        self.query_status_var = tk.StringVar(value=f"当前展示 {len(self.event_rows)} 条违规记录")

    def _build_layout(self):
        container = self._create_page_container()
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)
        container.grid_rowconfigure(3, weight=1)

        self._build_top_bar(container)
        self._build_summary_cards(container)
        self._build_middle_section(container)
        self._build_bottom_section(container)

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

    def _build_top_bar(self, parent):
        top_bar = tk.Frame(parent, bg=APP_BG)
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        top_bar.grid_columnconfigure(0, weight=1)

        left = tk.Frame(top_bar, bg=APP_BG)
        left.grid(row=0, column=0, sticky="w")
        tk.Label(
            left,
            text="停车场巡检小车上位机",
            bg=APP_BG,
            fg=TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 22, "bold"),
        ).pack(anchor="w")
        tk.Label(
            left,
            text="首页总览",
            bg=APP_BG,
            fg=TEXT_SECONDARY,
            font=("Microsoft YaHei UI", 10),
        ).pack(anchor="w", pady=(6, 0))

        right = tk.Frame(top_bar, bg=APP_BG)
        right.grid(row=0, column=1, sticky="e")
        self._build_status_chip(right, "小车在线", ACCENT_GREEN).pack(side="left", padx=(0, 12))
        self._build_status_chip(right, "数据库正常", ACCENT_BLUE).pack(side="left", padx=(0, 12))

        time_card = tk.Frame(right, bg=PANEL_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
        time_card.pack(side="left")
        tk.Label(
            time_card,
            textvariable=self.time_var,
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
            font=("Consolas", 11),
            padx=16,
            pady=10,
        ).pack()

    def _show_violation_alert(self):
        if self.alert_banner is not None:
            self.alert_banner.destroy()

        self.alert_message_var.set(
            f"违停提醒  {self.alert_event['plate']} 未按车位规范停车，存在压线情况，请及时处理"
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
            text="实时违规告警",
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
            text="持续监测中",
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
        if not hasattr(self, "event_tree"):
            return

        children = self.event_tree.get_children()
        if not children:
            return

        self.event_tree.selection_set(children[0])
        self.event_tree.focus(children[0])
        self.event_tree.see(children[0])

    def _build_status_chip(self, parent, text, color):
        chip = tk.Frame(parent, bg=PANEL_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
        dot = tk.Canvas(chip, width=12, height=12, bg=PANEL_BG, highlightthickness=0)
        dot.create_oval(2, 2, 10, 10, fill=color, outline=color)
        dot.pack(side="left", padx=(14, 8), pady=12)
        tk.Label(
            chip,
            text=text,
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 10, "bold"),
        ).pack(side="left", padx=(0, 14))
        return chip

    def _build_summary_cards(self, parent):
        row = tk.Frame(parent, bg=APP_BG)
        row.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        for index, item in enumerate(self.summary_data):
            row.grid_columnconfigure(index, weight=1)
            card = tk.Frame(row, bg=PANEL_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 10, 0))

            tk.Frame(card, bg=item["accent"], width=6).pack(side="left", fill="y")
            content = tk.Frame(card, bg=PANEL_BG)
            content.pack(side="left", fill="both", expand=True, padx=18, pady=16)

            title_label = tk.Label(content, text=item["title"], bg=PANEL_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 10))
            title_label.pack(anchor="w")
            value_label = tk.Label(content, text=item["value"], bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Microsoft YaHei UI", 24, "bold"), pady=8)
            value_label.pack(anchor="w")
            detail_label = tk.Label(content, text=item["detail"], bg=PANEL_BG, fg=item["accent"], font=("Microsoft YaHei UI", 9))
            detail_label.pack(anchor="w")
            self.summary_card_widgets.append({
                "value": value_label,
                "detail": detail_label,
                "accent": item["accent"],
            })

    def _build_middle_section(self, parent):
        middle = tk.Frame(parent, bg=APP_BG)
        middle.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        middle.grid_columnconfigure(0, weight=5)
        middle.grid_columnconfigure(1, weight=3)
        middle.grid_rowconfigure(0, weight=1)

        event_panel = tk.Frame(middle, bg=PANEL_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
        event_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._build_event_panel(event_panel)

        status_panel = tk.Frame(middle, bg=PANEL_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
        status_panel.grid(row=0, column=1, sticky="nsew")
        self._build_status_panel(status_panel)

    def _build_event_panel(self, parent):
        header = tk.Frame(parent, bg=PANEL_BG)
        header.pack(fill="x", padx=18, pady=(16, 10))
        header.grid_columnconfigure(1, weight=1)

        title_block = tk.Frame(header, bg=PANEL_BG)
        title_block.grid(row=0, column=0, sticky="w")
        tk.Label(title_block, text="最近违规事件", bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Microsoft YaHei UI", 14, "bold")).pack(anchor="w")
        tk.Label(title_block, text="展示最近违规事件与处理状态", bg=PANEL_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 9)).pack(anchor="w", pady=(4, 0))

        quick_query = tk.Frame(header, bg=CARD_ALT_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
        quick_query.grid(row=0, column=2, sticky="e", padx=(12, 0))

        entry = tk.Entry(
            quick_query,
            textvariable=self.search_var,
            bg=CARD_ALT_BG,
            fg=TEXT_SECONDARY,
            relief="flat",
            insertbackground=TEXT_PRIMARY,
            font=("Microsoft YaHei UI", 10),
            width=24,
        )
        entry.pack(side="left", padx=(12, 8), pady=10)
        entry.bind("<FocusIn>", self._clear_search_placeholder)
        entry.bind("<FocusOut>", self._restore_search_placeholder)
        entry.bind("<Return>", lambda _event: self._run_quick_query())

        tk.Button(
            quick_query,
            text="快速查询",
            command=self._run_quick_query,
            bg=ACCENT_BLUE,
            fg="#0b1120",
            activebackground="#67e8f9",
            activeforeground="#0b1120",
            relief="flat",
            bd=0,
            padx=16,
            pady=8,
            font=("Microsoft YaHei UI", 9, "bold"),
            cursor="hand2",
        ).pack(side="left", padx=(0, 10), pady=6)
        tk.Button(
            quick_query,
            text="进入违规事件页",
            command=open_violation_events_page,
            bg=ACCENT_ORANGE,
            fg="#271504",
            activebackground="#fbbf24",
            activeforeground="#271504",
            relief="flat",
            bd=0,
            padx=16,
            pady=8,
            font=("Microsoft YaHei UI", 9, "bold"),
            cursor="hand2",
        ).pack(side="left", padx=(0, 10), pady=6)

        tk.Label(
            parent,
            textvariable=self.query_status_var,
            bg=PANEL_BG,
            fg=ACCENT_BLUE,
            font=("Microsoft YaHei UI", 9),
        ).pack(anchor="w", padx=18, pady=(0, 10))

        columns = ("event_id", "plate", "type", "time", "area", "status")
        table_frame = tk.Frame(parent, bg=PANEL_BG)
        table_frame.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        tree_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        self.event_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Dashboard.Treeview",
            yscrollcommand=tree_scrollbar.set,
        )
        tree_scrollbar.config(command=self.event_tree.yview)

        self.event_tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")

        headings = {
            "event_id": "事件编号",
            "plate": "车牌号",
            "type": "违规类型",
            "time": "发现时间",
            "area": "区域",
            "status": "状态",
        }
        widths = {
            "event_id": 150,
            "plate": 110,
            "type": 120,
            "time": 170,
            "area": 90,
            "status": 90,
        }

        for column in columns:
            self.event_tree.heading(column, text=headings[column])
            self.event_tree.column(column, width=widths[column], anchor="center", stretch=(column == "time"))

        self._populate_event_table(self.event_rows)

    def _populate_event_table(self, rows):
        self.event_tree.delete(*self.event_tree.get_children())
        for index, item in enumerate(rows):
            row_tags = ["evenrow" if index % 2 == 0 else "oddrow"]
            if item[1] == self.alert_event["plate"]:
                row_tags.append("alertrow")
            self.event_tree.insert("", "end", values=item, tags=tuple(row_tags))

        self.event_tree.tag_configure("evenrow", background=CARD_BG)
        self.event_tree.tag_configure("oddrow", background="#1b2432")
        self.event_tree.tag_configure("alertrow", background="#4c0519", foreground="#fee2e2")
        self._highlight_primary_event()

    def _build_status_panel(self, parent):
        tk.Label(parent, text="小车状态概览", bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Microsoft YaHei UI", 14, "bold")).pack(anchor="w", padx=18, pady=(16, 4))
        tk.Label(parent, text="设备在线状态、任务进度和当前运行摘要", bg=PANEL_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 9)).pack(anchor="w", padx=18, pady=(0, 10))

        status_box = tk.Frame(parent, bg=PANEL_BG)
        status_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        for label, value in self.robot_status:
            row = tk.Frame(status_box, bg=CARD_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=label, bg=CARD_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 10), padx=14, pady=12).pack(side="left")
            tk.Label(row, text=value, bg=CARD_BG, fg=TEXT_PRIMARY, font=("Microsoft YaHei UI", 10, "bold"), padx=14, pady=12).pack(side="right")

        footer = tk.Frame(parent, bg=CARD_ALT_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
        footer.pack(fill="x", padx=18, pady=(0, 18))
        tk.Label(
            footer,
            text="当前显示设备状态、任务进度和处理提醒。",
            bg=CARD_ALT_BG,
            fg=ACCENT_PURPLE,
            font=("Microsoft YaHei UI", 9),
            padx=14,
            pady=12,
            justify="left",
            wraplength=320,
        ).pack(anchor="w")

    def _build_bottom_section(self, parent):
        bottom = tk.Frame(parent, bg=APP_BG)
        bottom.grid(row=3, column=0, sticky="nsew")
        bottom.grid_columnconfigure(0, weight=3)
        bottom.grid_columnconfigure(1, weight=2)
        bottom.grid_rowconfigure(0, weight=1)

        log_panel = tk.Frame(bottom, bg=PANEL_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
        log_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._build_log_panel(log_panel)

        trend_panel = tk.Frame(bottom, bg=PANEL_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
        trend_panel.grid(row=0, column=1, sticky="nsew")
        self._build_trend_panel(trend_panel)

    def _build_log_panel(self, parent):
        tk.Label(parent, text="系统动态", bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Microsoft YaHei UI", 14, "bold")).pack(anchor="w", padx=18, pady=(16, 4))
        tk.Label(parent, text="最近状态变化和事件处理摘要", bg=PANEL_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 9)).pack(anchor="w", padx=18, pady=(0, 12))

        self.log_panel_body = tk.Frame(parent, bg=PANEL_BG)
        self.log_panel_body.pack(fill="both", expand=True)
        self._render_logs()

    def _build_trend_panel(self, parent):
        tk.Label(parent, text="今日巡检摘要", bg=PANEL_BG, fg=TEXT_PRIMARY, font=("Microsoft YaHei UI", 14, "bold")).pack(anchor="w", padx=18, pady=(16, 4))
        tk.Label(parent, text="展示今日巡检任务与处理情况", bg=PANEL_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 9)).pack(anchor="w", padx=18, pady=(0, 10))

        summary_box = tk.Frame(parent, bg=PANEL_BG)
        summary_box.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        for label, value in self.trend_data:
            block = tk.Frame(summary_box, bg=CARD_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
            block.pack(fill="x", pady=6)
            tk.Label(block, text=label, bg=CARD_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 10), padx=14, pady=12).pack(anchor="w")
            value_label = tk.Label(block, text=value, bg=CARD_BG, fg=TEXT_PRIMARY, font=("Microsoft YaHei UI", 12, "bold"), padx=14)
            value_label.pack(anchor="w", pady=(0, 12))
            self.trend_value_labels[label] = value_label

    def _render_logs(self):
        if not hasattr(self, "log_panel_body"):
            return

        for item in self.log_panel_body.winfo_children():
            item.destroy()

        for time_text, source, message in self.system_logs:
            item = tk.Frame(self.log_panel_body, bg=CARD_BG, highlightbackground=LINE_COLOR, highlightthickness=1)
            item.pack(fill="x", padx=18, pady=6)

            top = tk.Frame(item, bg=CARD_BG)
            top.pack(fill="x", padx=14, pady=(10, 0))
            tk.Label(top, text=time_text, bg=CARD_BG, fg=ACCENT_BLUE, font=("Consolas", 10, "bold")).pack(side="left")
            tk.Label(top, text=source, bg=CARD_BG, fg=TEXT_SECONDARY, font=("Microsoft YaHei UI", 9)).pack(side="right")
            tk.Label(
                item,
                text=message,
                bg=CARD_BG,
                fg=TEXT_PRIMARY,
                font=("Microsoft YaHei UI", 10),
                wraplength=760,
                justify="left",
                padx=14,
                pady=10,
            ).pack(anchor="w")

    def _refresh_dashboard_view(self):
        self.summary_data = build_summary_data(self.dashboard_state)
        self.event_rows = build_event_rows(self.dashboard_state)
        self.robot_status = build_robot_status(self.dashboard_state)
        self.system_logs = build_system_logs(self.dashboard_state)
        self.trend_data = build_trend_data(self.dashboard_state)

        for widget_map, item in zip(self.summary_card_widgets, self.summary_data):
            widget_map["value"].configure(text=item["value"])
            widget_map["detail"].configure(text=item["detail"], fg=item["accent"])

        for label, value in self.robot_status:
            if label in self.status_value_labels:
                self.status_value_labels[label].configure(text=value)

        for label, value in self.trend_data:
            if label in self.trend_value_labels:
                self.trend_value_labels[label].configure(text=value)

        self._render_logs()

        keyword = self.search_var.get().strip()
        if keyword and keyword != "输入车牌号快速查询":
            self._run_quick_query()
        else:
            self._populate_event_table(self.event_rows)
            self.query_status_var.set(f"当前展示 {len(self.event_rows)} 条违规记录")

    def _append_system_log(self, source, message):
        self.dashboard_state["system_logs"].insert(0, {
            "time": datetime.now(),
            "source": source,
            "message": message,
        })
        self.dashboard_state["system_logs"] = self.dashboard_state["system_logs"][:6]

    def _push_new_event(self, plate=None, violation_type=None, area=None, status="未处理"):
        now = datetime.now()
        event_id = f"P{now.strftime('%Y%m%d')}{self.dashboard_state['next_event_index']:03d}"
        self.dashboard_state["next_event_index"] += 1

        record = make_event_record(
            event_id,
            plate or random_plate(),
            violation_type or random.choice(VIOLATION_TYPES),
            now,
            area or random_area_slot(),
            status,
        )
        self.dashboard_state["event_records"].insert(0, record)
        self.dashboard_state["event_records"] = self.dashboard_state["event_records"][:8]
        return record

    def _schedule_realtime_update(self):
        self._simulate_realtime_update()
        self.realtime_update_after = self.root.after(3000, self._schedule_realtime_update)

    def _simulate_realtime_update(self):
        state = self.dashboard_state
        state["tick_count"] += 1
        tick = state["tick_count"]

        state["heartbeat_sec"] = random.randint(1, 4)
        state["patrol_seconds"] += 3
        state["mileage_km"] = round(min(9.9, state["mileage_km"] + random.choice([0.0, 0.0, 0.1])), 1)

        if state["task_state"] == "巡检中":
            state["task_progress"] = min(99, state["task_progress"] + random.choice([0, 1]))
        elif random.random() < 0.25:
            state["task_state"] = "巡检中"

        if tick % 6 == 0 and state["battery"] > 45:
            state["battery"] -= 1

        if tick % 5 == 0 and random.random() < 0.4:
            state["current_area"] = f"{random.choice(AREAS)} {random.choice(ZONE_TEXT)}"
            self._append_system_log("巡检", f"巡检位置更新至 {state['current_area']}。")

        if tick % 8 == 0 and state["pending_events"] > 1 and random.random() < 0.55:
            for item in reversed(state["event_records"]):
                if item["status"] == "未处理" and item["plate"] != self.alert_event["plate"]:
                    item["status"] = "已通知"
                    state["pending_events"] -= 1
                    state["handled_events"] += 1
                    self._append_system_log("事件", f"{item['plate']} 已完成通知，等待现场复核。")
                    break

        if tick % 10 == 0 and random.random() < 0.5:
            state["owners_count"] += 1
            self._append_system_log("数据库", f"新增同步 1 条车辆信息，当前共 {state['owners_count']} 条。")

        created_event = None
        if tick % 7 == 0 and random.random() < 0.45:
            created_event = self._push_new_event(status="未处理")
            state["total_events"] += 1
            state["pending_events"] = min(state["pending_events"] + 1, state["total_events"])
            state["handled_events"] = state["total_events"] - state["pending_events"]
            state["recent_new_events"] = min(3, state["recent_new_events"] + 1)
            self._append_system_log("事件", f"检测到新违规车辆：{created_event['plate']}，位置 {created_event['area']}。")
        else:
            state["recent_new_events"] = max(0, state["recent_new_events"] - 1)

        state["high_priority"] = min(state["pending_events"], max(0, state["high_priority"] + random.choice([-1, 0, 0, 1])))
        state["abnormal_count"] = 1 if random.random() < 0.08 else 0
        state["network_status"] = random.choices(NETWORK_CHOICES, weights=[7, 2, 1], k=1)[0]
        state["serial_status"] = random.choices(SERIAL_CHOICES, weights=[7, 2, 1], k=1)[0]

        if created_event is None and tick % 9 == 0 and random.random() < 0.35:
            self._append_system_log("小车", f"当前任务状态：{state['task_state']}，续航预计可支持后续巡检。")

        self._refresh_dashboard_view()

    def _run_quick_query(self):
        keyword = self.search_var.get().strip()
        if not keyword or keyword == "输入车牌号快速查询":
            self._populate_event_table(self.event_rows)
            self.query_status_var.set(f"当前展示 {len(self.event_rows)} 条违规记录")
            return

        keyword_upper = keyword.upper()
        filtered_rows = [item for item in self.event_rows if keyword_upper in item[1].upper()]
        self._populate_event_table(filtered_rows)

        if filtered_rows:
            self.query_status_var.set(f"已查询到 {keyword} 相关 {len(filtered_rows)} 条违规记录")
        else:
            self.query_status_var.set(f"未找到 {keyword} 对应的违规记录")

    def _clear_search_placeholder(self, _event):
        if self.search_var.get() == "输入车牌号快速查询":
            self.search_var.set("")

    def _restore_search_placeholder(self, _event):
        if not self.search_var.get().strip():
            self.search_var.set("输入车牌号快速查询")

    def _update_clock(self):
        self.time_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        if self.dashboard_state:
            self.dashboard_state["heartbeat_sec"] = min(self.dashboard_state.get("heartbeat_sec", 1) + 1, 9)
            self.summary_data = build_summary_data(self.dashboard_state)
            if len(self.summary_card_widgets) >= 3:
                self.summary_card_widgets[2]["detail"].configure(text=self.summary_data[2]["detail"], fg=self.summary_data[2]["accent"])
        self.root.after(1000, self._update_clock)


def main():
    root = tk.Tk()
    HomePageApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


