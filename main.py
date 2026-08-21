"""
Minimal, düşük kaynak kullanımlı webcam hand-tracking uygulaması.

Akış: Webcam -> el algılama -> işaret parmağı ucu koordinatı -> basit daire teması

Tasarım kararları (RAM/CPU öncelikli):
- Tek el takibi (num_hands=1)
- Kamera 640x480 @ 30 FPS
- Hand tracking ~15 FPS (kameranın her 2 frame'inde bir)
- Thread yok: kamera okuma + tracking + çizim tek döngüde, basit tutuldu
- Görüntüyü Tkinter'a aktarmak için Pillow yerine ham PPM byte dönüşümü kullanılıyor
"""

import cv2
import tkinter as tk
from tkinter import messagebox

from hand_tracker import HandTracker

CAM_WIDTH = 640
CAM_HEIGHT = 480
CAM_FPS = 30
TRACK_EVERY_N_FRAMES = 2  # kamera 30 FPS -> tracking ~15 FPS

COLOR_NORMAL = (80, 80, 200)   # BGR - dokunulmamış daire
COLOR_HOVER = (60, 200, 60)    # BGR - temas edilen daire


def make_circles():
    return [
        {"cx": 150, "cy": 240, "radius": 40, "hover": False},
        {"cx": 320, "cy": 240, "radius": 40, "hover": False},
        {"cx": 490, "cy": 240, "radius": 40, "hover": False},
    ]


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Tracking - Minimal")
        self.root.resizable(False, False)

        self.cap = None
        self.tracker = None
        self.running = False
        self.frame_count = 0
        self.last_finger_pos = None  # tracking çalışmayan frame'lerde son bilinen konum
        self.circles = make_circles()
        self._photo_ref = None  # PhotoImage'in garbage collect edilmesini önlemek için

        self.video_label = tk.Label(root, bg="black")
        self.video_label.pack()

        self.button = tk.Button(root, text="Start Camera", width=20, command=self.toggle_camera)
        self.button.pack(pady=6)

        self.status_label = tk.Label(root, text="Kamera kapalı", fg="gray")
        self.status_label.pack(pady=(0, 6))

    # ---------- kamera kontrolü ----------

    def toggle_camera(self):
        if self.running:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if self.cap is None or not self.cap.isOpened():
            messagebox.showerror("Hata", "Webcam bulunamadı.")
            self.cap = None
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAM_FPS)

        ok, _ = self.cap.read()
        if not ok:
            messagebox.showerror("Hata", "Webcam erişimine izin verilmedi.")
            self.cap.release()
            self.cap = None
            return

        try:
            self.tracker = HandTracker()
        except FileNotFoundError as e:
            messagebox.showerror("Model dosyası eksik", str(e))
            self.cap.release()
            self.cap = None
            return

        self.running = True
        self.frame_count = 0
        self.last_finger_pos = None
        self.circles = make_circles()
        self.button.config(text="Stop Camera")
        self.status_label.config(text="Kamera açık", fg="green")
        self.update_frame()

    def stop_camera(self):
        self.running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if self.tracker is not None:
            self.tracker.close()
            self.tracker = None
        self.video_label.configure(image="")
        self._photo_ref = None
        self.button.config(text="Start Camera")
        self.status_label.config(text="Kamera kapalı", fg="gray")

    # ---------- ana döngü ----------

    def update_frame(self):
        if not self.running or self.cap is None:
            return

        ok, frame = self.cap.read()
        if not ok:
            messagebox.showerror("Hata", "Webcam bulunamadı.")
            self.stop_camera()
            return

        frame = cv2.flip(frame, 1)  # ayna görüntüsü (doğal etkileşim için)
        self.frame_count += 1

        if self.frame_count % TRACK_EVERY_N_FRAMES == 0:
            self.last_finger_pos = self.tracker.get_index_fingertip(frame)

        self._update_circles(self.last_finger_pos)
        self._draw_overlay(frame, self.last_finger_pos)
        self._show_frame(frame)

        delay_ms = int(1000 / CAM_FPS)
        self.root.after(delay_ms, self.update_frame)

    def _update_circles(self, finger_pos):
        for c in self.circles:
            if finger_pos is None:
                c["hover"] = False
                continue
            dx = finger_pos[0] - c["cx"]
            dy = finger_pos[1] - c["cy"]
            c["hover"] = (dx * dx + dy * dy) < (c["radius"] * c["radius"])

    def _draw_overlay(self, frame, finger_pos):
        for c in self.circles:
            color = COLOR_HOVER if c["hover"] else COLOR_NORMAL
            thickness = -1 if c["hover"] else 2
            cv2.circle(frame, (c["cx"], c["cy"]), c["radius"], color, thickness)

        if finger_pos is not None:
            cv2.circle(frame, finger_pos, 8, (0, 0, 255), -1)

    def _show_frame(self, frame):
        # BGR -> RGB ve Pillow olmadan doğrudan PPM formatına çevirip Tkinter'a veriyoruz
        rgb = frame[:, :, ::-1]
        h, w = rgb.shape[:2]
        header = f"P6\n{w} {h}\n255\n".encode("ascii")
        photo = tk.PhotoImage(data=header + rgb.tobytes(), format="PPM")
        self.video_label.configure(image=photo)
        self._photo_ref = photo  # referansı tut, yoksa görüntü hemen kaybolur

    def on_close(self):
        self.stop_camera()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
