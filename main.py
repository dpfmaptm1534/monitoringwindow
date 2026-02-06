import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
import pytesseract
from mss import mss
import pygetwindow as gw
import threading
import time
import ctypes
import sys
import re
import winsound 

# ==============================================================
# [설정] Tesseract 경로
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# ==============================================================

# 관리자 권한 획득
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join([sys.argv[0]] + sys.argv[1:]), None, 1)
    sys.exit()

try: ctypes.windll.user32.SetProcessDPIAware()
except: pass

def extract_number(text):
    try:
        clean = text.replace(',', '')
        match = re.search(r"[-+]?\d*\.\d+|\d+", clean)
        return float(match.group()) if match else None
    except: return None

def color_diff(c1, c2):
    return np.sqrt(np.sum((np.array(c1) - np.array(c2)) ** 2))

class UniversalMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("만능 화면 감시기 (팝업 알림 버전)")
        self.root.geometry("900x600")

        self.target_title = None
        self.monitors = [] 
        self.is_running = False
        self.is_selecting = False
        
        # 알림 설정 변수
        self.sound_enabled = tk.BooleanVar(value=False) # 스피커 없으므로 기본 OFF
        self.popup_enabled = tk.BooleanVar(value=True)  # 팝업 기본 ON
        
        self.alert_window = None # 현재 떠있는 경고창

        self.select_target_window()
        self.setup_ui()
        self.start_thread()

    def select_target_window(self):
        titles = sorted([t for t in gw.getAllTitles() if t.strip()])
        top = tk.Toplevel(self.root)
        top.title("감시 대상 선택")
        top.geometry("300x400")
        top.attributes('-topmost', True)

        lb = tk.Listbox(top, font=("맑은 고딕", 10))
        lb.pack(fill="both", expand=True, padx=5, pady=5)
        for t in titles: lb.insert(tk.END, t)

        def on_select():
            try:
                self.target_title = lb.get(lb.curselection()[0])
                top.destroy()
                self.root.deiconify()
            except: pass

        tk.Button(top, text="선택 완료", command=on_select, bg="#ffcc00").pack(fill="x", pady=5)
        self.root.withdraw()
        self.root.wait_window(top)
        if not self.target_title: sys.exit()

    def setup_ui(self):
        # 상단 컨트롤 패널
        ctrl_frame = tk.Frame(self.root, pady=10, bg="#444")
        ctrl_frame.pack(fill="x")

        tk.Button(ctrl_frame, text="+ 감시 추가", command=self.add_row, 
                  bg="#00d2ff", fg="black", font=("맑은 고딕", 10, "bold"), width=12).pack(side="left", padx=10)
        
        # 알림 옵션 체크박스들
        tk.Checkbutton(ctrl_frame, text="팝업 알림 켜기", variable=self.popup_enabled, 
                       bg="#444", fg="#00ff00", selectcolor="#444", font=("맑은 고딕", 10, "bold")).pack(side="left", padx=10)

        tk.Checkbutton(ctrl_frame, text="소리 알림 켜기", variable=self.sound_enabled, 
                       bg="#444", fg="white", selectcolor="#444").pack(side="left", padx=5)

        tk.Label(ctrl_frame, text=f"타겟: {self.target_title}", fg="white", bg="#444").pack(side="right", padx=10)

        # 헤더
        h_frame = tk.Frame(self.root, bg="#ddd", pady=3)
        h_frame.pack(fill="x", padx=5)
        cols = [("이름", 10), ("현재값 / 상태", 20), ("감시 모드", 15), ("조건(Target)", 10), ("추가값", 8), ("설정", 8)]
        for txt, w in cols:
            tk.Label(h_frame, text=txt, width=w, bg="#ddd", font=("맑은 고딕", 9, "bold")).pack(side="left", padx=2)

        # 스크롤 영역
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas)

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def add_row(self):
        idx = len(self.monitors)
        row = tk.Frame(self.scroll_frame, pady=5, bd=1, relief="solid", bg="#f9f9f9")
        row.pack(fill="x", padx=5, pady=2)

        name_ent = tk.Entry(row, width=10, justify="center")
        name_ent.insert(0, f"항목 {idx+1}")
        name_ent.pack(side="left", padx=2)

        val_lbl = tk.Label(row, text="[대기]", width=22, bg="#eee", relief="sunken")
        val_lbl.pack(side="left", padx=2)

        modes = [
            "숫자 < 미만 (Alert if <)", 
            "숫자 > 초과 (Alert if >)", 
            "숫자 = 일치 (Equal)", 
            "숫자 범위 밖 (Out of Range)",
            "텍스트 포함 (Contains)", 
            "텍스트 불일치 (Not Equal)",
            "색상 변화 (Color Change)"
        ]
        mode_cb = ttk.Combobox(row, values=modes, width=22, state="readonly")
        mode_cb.current(1)
        mode_cb.pack(side="left", padx=2)

        target1 = tk.Entry(row, width=12, justify="center")
        target1.pack(side="left", padx=2)

        target2 = tk.Entry(row, width=10, justify="center")
        target2.pack(side="left", padx=2)

        btn = tk.Button(row, text="영역 잡기", command=lambda i=idx: self.set_roi(i), bg="#ffcc00")
        btn.pack(side="right", padx=5)

        self.monitors.append({
            "widgets": [name_ent, val_lbl, mode_cb, target1, target2],
            "roi": None,
            "base_color": None, 
            "last_alert": 0
        })

    def set_roi(self, idx):
        self.is_selecting = True
        time.sleep(0.2)
        try:
            wins = gw.getWindowsWithTitle(self.target_title)
            if not wins: return
            win = wins[0]
            if win.isMinimized: win.restore()
            win.activate()
            time.sleep(0.5)

            with mss() as sct:
                rect = {'top': win.top, 'left': win.left, 'width': win.width, 'height': win.height}
                img = np.array(sct.grab(rect))
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            r = cv2.selectROI("Area Selector", img, showCrosshair=True)
            cv2.destroyWindow("Area Selector")

            if r[2] > 0 and r[3] > 0:
                roi_data = (int(r[0]), int(r[1]), int(r[2]), int(r[3]))
                self.monitors[idx]['roi'] = roi_data
                
                roi_img = img[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
                avg_color = np.mean(roi_img, axis=(0, 1))
                self.monitors[idx]['base_color'] = avg_color
                
                self.monitors[idx]['widgets'][1].config(text="영역 설정됨", bg="#d0f0c0")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.is_selecting = False

    def start_thread(self):
        self.is_running = True
        t = threading.Thread(target=self.loop)
        t.daemon = True
        t.start()

    def show_popup_alert(self, title, message):
        """빨간색 경고 팝업창 띄우기 (중복 방지)"""
        if self.alert_window is not None:
            return # 이미 창이 떠있으면 새로 안 만듦

        def close_alert():
            if self.alert_window:
                self.alert_window.destroy()
                self.alert_window = None

        top = tk.Toplevel(self.root)
        top.title("⚠️ 경고 ⚠️")
        top.geometry("400x200")
        top.configure(bg="red")
        top.attributes('-topmost', True) # 항상 맨 위에
        
        # 화면 중앙 배치
        x = (self.root.winfo_screenwidth() // 2) - 200
        y = (self.root.winfo_screenheight() // 2) - 100
        top.geometry(f"+{x}+{y}")

        tk.Label(top, text=f"🚨 {title} 🚨", bg="red", fg="white", font=("맑은 고딕", 20, "bold")).pack(pady=20)
        tk.Label(top, text=message, bg="red", fg="yellow", font=("맑은 고딕", 14, "bold")).pack(pady=10)
        
        tk.Button(top, text="확인 (닫기)", command=close_alert, bg="white", font=("bold", 12)).pack(pady=20)
        
        top.protocol("WM_DELETE_WINDOW", close_alert) # X 버튼 눌러도 초기화
        self.alert_window = top

    def loop(self):
        with mss() as sct:
            while self.is_running:
                if self.is_selecting:
                    time.sleep(0.5); continue

                try:
                    wins = gw.getWindowsWithTitle(self.target_title)
                    if not wins: time.sleep(1); continue
                    win = wins[0]
                    if win.isMinimized: time.sleep(0.5); continue

                    current_mons = list(self.monitors)
                    any_alert_triggered = False # 이번 루프에서 알람이 있었는지 체크

                    for item in current_mons:
                        roi = item['roi']
                        if not roi: continue
                        
                        name_ent, val_lbl, mode_cb, t1_ent, t2_ent = item['widgets']
                        item_name = name_ent.get()
                        mode = mode_cb.get()
                        
                        rx, ry, rw, rh = roi
                        mon_area = {'top': win.top + ry, 'left': win.left + rx, 'width': rw, 'height': rh}
                        img = np.array(sct.grab(mon_area))
                        
                        is_alert = False
                        display_txt = ""

                        # [A] 색상
                        if "색상" in mode:
                            curr_img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                            curr_color = np.mean(curr_img, axis=(0, 1))
                            base_color = item['base_color']
                            if base_color is not None:
                                diff = color_diff(curr_color, base_color)
                                t_val = t1_ent.get().strip()
                                threshold = float(t_val) if t_val else 30.0
                                is_alert = diff > threshold
                                display_txt = f"차이: {diff:.1f}"

                        # [B] OCR
                        else:
                            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
                            text = pytesseract.image_to_string(gray, lang='eng+kor', config='--psm 7').strip()
                            display_txt = text if text else "..."
                            
                            v1_str = t1_ent.get().strip()
                            v2_str = t2_ent.get().strip()

                            if "숫자" in mode:
                                curr_num = extract_number(text)
                                if curr_num is not None and v1_str:
                                    try:
                                        v1 = float(v1_str)
                                        if "미만" in mode and curr_num < v1: is_alert = True
                                        elif "초과" in mode and curr_num > v1: is_alert = True
                                        elif "일치" in mode and curr_num == v1: is_alert = True
                                        elif "범위 밖" in mode and v2_str:
                                            v2 = float(v2_str)
                                            if not (v1 <= curr_num <= v2): is_alert = True
                                    except: pass
                            elif "텍스트" in mode:
                                if "포함" in mode and v1_str:
                                    if v1_str in text: is_alert = True
                                elif "불일치" in mode and v1_str:
                                    if v1_str != text: is_alert = True

                        self.update_ui(val_lbl, display_txt, is_alert)

                        # 알림 조건 만족 시 팝업 띄우기
                        if is_alert:
                            any_alert_triggered = True
                            if self.popup_enabled.get():
                                # 메인 스레드 충돌 방지를 위해 after 사용
                                self.root.after(0, lambda: self.show_popup_alert(item_name, f"현재값: {display_txt}"))

                    # 소리 알림 (팝업과는 별도로 작동)
                    if any_alert_triggered and self.sound_enabled.get():
                        winsound.Beep(1000, 100)

                    time.sleep(0.1)

                except Exception as e:
                    print(f"Loop Err: {e}")
                    time.sleep(1)

    def update_ui(self, label, text, alert):
        color = "#ff5555" if alert else "#f0f0f0"
        fg_color = "white" if alert else "black"
        if len(text) > 15: text = text[:15] + ".."
        label.config(text=text, bg=color, fg=fg_color)

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalMonitor(root)
    root.mainloop()