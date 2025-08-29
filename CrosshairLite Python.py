from __future__ import annotations
import json
import os
import sys
import math
from dataclasses import dataclass, asdict, field
from typing import Dict, List

from PySide6.QtCore import Qt, QRect, QPoint, QSize, QTimer, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QAction, QIcon, QPixmap, QImage, QPolygon
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QLineEdit, QPushButton, QComboBox, QSystemTrayIcon, QMenu,
    QDoubleSpinBox, QSpinBox, QStyle, QTabWidget, QGroupBox, QFormLayout,
    QMessageBox, QDialog, QDialogButtonBox, QListWidget, QListWidgetItem, QCheckBox, QInputDialog, QGridLayout, QSizePolicy
)

# =========================== Глобальная чёрная тема (QSS) ===========================
DARK_QSS = """
* { color: #E6E6E6; font-size: 13px; }
QMainWindow, QWidget { background: #0B0C0F; }
QGroupBox { border: 1px solid #1A1B20; border-radius: 12px; margin-top: 12px; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 2px 6px; color: #9AA0A6; }
QPushButton { background: #121318; border: 1px solid #21232A; border-radius: 10px; padding: 8px 12px; }
QPushButton:hover { background: #17181F; }
QPushButton:pressed { background: #0F1014; }
QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox { background: #0F1014; border: 1px solid #1A1B20; border-radius: 10px; padding: 6px 8px; }
QSlider::groove:horizontal { height: 8px; background: #1A1B20; border-radius: 4px; }
QSlider::handle:horizontal { width: 16px; background: #5AA9FF; border-radius: 8px; margin: -6px 0; }
QSlider::groove:vertical { width: 8px; background: #1A1B20; border-radius: 4px; }
QSlider::handle:vertical { height: 16px; background: #5AA9FF; border-radius: 8px; margin: 0 -6px; }
QTabWidget::pane { border: 1px solid #1A1B20; border-radius: 12px; top: -1px; }
QTabBar::tab { background: #0F1014; border: 1px solid #1A1B20; padding: 8px 14px; border-top-left-radius: 12px; border-top-right-radius: 12px; margin-right: 4px; }
QTabBar::tab:selected { background: #14161B; }
QMenu { background: #0B0C0F; border: 1px solid #1A1B20; border-radius: 12px; padding: 6px; }
QMenu::separator { height: 1px; background: #1A1B20; margin: 6px 8px; }
QMenu::item { padding: 6px 12px; border-radius: 8px; }
QMenu::item:selected { background: #17181F; }
QComboBox QAbstractItemView { background: #0F1014; border: 1px solid #1A1B20; border-radius: 10px; selection-background-color: #17181F; }
QToolTip { background: #0F1014; color: #E6E6E6; border: 1px solid #1A1B20; border-radius: 8px; }
QDialog { background: #0B0C0F; border: 1px solid #1A1B20; border-radius: 14px; }
"""

# =========================== Модель настроек ===========================
@dataclass
class Settings:
    # Прицел
    style: str = "Cross"  # Dot | Cross | Circle | CrossCircle
    color_hex: str = "#00FF00"
    opacity: float = 1.0  # 0..1
    thickness: int = 2
    length: int = 24
    gap: int = 6
    radius: int = 18
    offset_x: int = 0
    offset_y: int = 0
    scale: float = 1.0

    # Вид
    canvas_size: int = 600
    visible: bool = True
    auto_apply: bool = True

    # Сцены (пресеты + состав сцены)
    scenes: Dict[str, dict] = field(default_factory=dict)
    active_scene: str = "Default"

    @staticmethod
    def path() -> str:
        base = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
        return os.path.join(base, "settings.json")

    @classmethod
    def load(cls) -> "Settings":
        try:
            with open(cls.path(), "r", encoding="utf-8") as f:
                raw = json.load(f)
            s = cls(**{k: v for k, v in raw.items() if k in cls.__dataclass_fields__})
            if s.scenes and s.active_scene in s.scenes:
                s.apply_scene_to_self(s.active_scene)
            else:
                s.scenes.setdefault("Default", s.scene_from_self())
                s.active_scene = "Default"
            # нормализуем сцены
            for name, data in s.scenes.items():
                data.setdefault("objects", [])
                data.setdefault("hide_crosshair", False if name == "Default" else True)
            return s
        except Exception:
            s = cls()
            s.scenes.setdefault("Default", s.scene_from_self())
            return s

    def save(self) -> None:
        try:
            with open(self.path(), "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ----- Сцены -----
    def scene_from_self(self) -> dict:
        cur = self.scenes.get(self.active_scene, {})
        return {
            "style": self.style,
            "color_hex": self.color_hex,
            "opacity": self.opacity,
            "thickness": self.thickness,
            "length": self.length,
            "gap": self.gap,
            "radius": self.radius,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "scale": self.scale,
            "objects": list(cur.get("objects", [])),
            "hide_crosshair": bool(cur.get("hide_crosshair", False)),
        }

    def apply_scene_to_self(self, name: str):
        data = self.scenes.get(name, {})
        self.style      = data.get("style", self.style)
        self.color_hex  = data.get("color_hex", self.color_hex)
        self.opacity    = float(data.get("opacity", self.opacity))
        self.thickness  = int(data.get("thickness", self.thickness))
        self.length     = int(data.get("length", self.length))
        self.gap        = int(data.get("gap", self.gap))
        self.radius     = int(data.get("radius", self.radius))
        self.offset_x   = int(data.get("offset_x", self.offset_x))
        self.offset_y   = int(data.get("offset_y", self.offset_y))
        self.scale      = float(data.get("scale", self.scale))
        data.setdefault("objects", [])
        data.setdefault("hide_crosshair", False if name == "Default" else True)
        self.scenes[name] = data
        self.active_scene = name

    def current_objects(self) -> List[dict]:
        sc = self.scenes.get(self.active_scene, {})
        return list(sc.get("objects", []))

    def set_current_objects(self, objs: List[dict]):
        sc = self.scenes.setdefault(self.active_scene, {})
        sc["objects"] = objs

    def scene_hide_crosshair(self) -> bool:
        sc = self.scenes.get(self.active_scene, {})
        return bool(sc.get("hide_crosshair", False))


# =========================== Цветовой круг (HSV) ===========================
class HSVWheel(QWidget):
    colorChanged = Signal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(180, 180)
        self._img: QImage | None = None
        self._h = 0.333; self._s = 1.0; self._v = 1.0

    def sizeHint(self): return QSize(220, 220)
    def setHSV(self, h: float, s: float, v: float):
        self._h = max(0.0, min(1.0, h)); self._s = max(0.0, min(1.0, s)); self._v = max(0.0, min(1.0, v)); self.update()
    def color(self) -> QColor: return QColor.fromHsvF(self._h, self._s, self._v, 1.0)
    def setColor(self, c: QColor):
        h, s, v, _ = c.getHsvF();  
        if h < 0: h = self._h
        self._h, self._s, self._v = h, s, v; self.update()
    def _rebuild(self, size: int):
        img = QImage(size, size, QImage.Format_ARGB32_Premultiplied); img.fill(Qt.transparent)
        R = (size - 2) / 2.0; cx = cy = size / 2.0
        for y in range(size):
            dy = y - cy
            for x in range(size):
                dx = x - cx; r = math.hypot(dx, dy)
                if r <= R:
                    s = r / R; ang = math.atan2(dy, dx); h = (ang + 2*math.pi) % (2*math.pi); h /= 2*math.pi
                    img.setPixelColor(x, y, QColor.fromHsvF(h, s, self._v, 1.0))
        self._img = img
    def resizeEvent(self, _):
        size = max(160, min(self.width(), self.height())); self._rebuild(size)
    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing, True)
        if self._img is not None:
            side = min(self.width(), self.height()); x = (self.width() - side)//2; y = (self.height() - side)//2
            p.drawImage(QRect(x, y, side, side), self._img)
            R = side/2; cx = x+R; cy = y+R
            px = cx + math.cos(self._h*2*math.pi) * (self._s*(R-1))
            py = cy + math.sin(self._h*2*math.pi) * (self._s*(R-1))
            p.setPen(QPen(Qt.white, 2)); p.setBrush(Qt.NoBrush); p.drawEllipse(QPoint(int(px), int(py)), 6, 6)
    def _pick(self, pos):
        side = min(self.width(), self.height()); x0 = (self.width()-side)//2; y0 = (self.height()-side)//2
        cx = x0 + side/2; cy = y0 + side/2; dx = pos.x()-cx; dy = pos.y()-cy; R = side/2; r = math.hypot(dx, dy)
        if r <= R:
            s = max(0.0, min(1.0, r/R)); h = (math.atan2(dy, dx) + 2*math.pi)%(2*math.pi); h /= 2*math.pi
            self._h, self._s = h, s; self.colorChanged.emit(self.color()); self.update()
    def mousePressEvent(self, e): self._pick(e.position().toPoint())
    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton: self._pick(e.position().toPoint())

# =========================== Диалог палитры ===========================
class ColorDialog(QDialog):
    def __init__(self, base_color: QColor, alpha: float, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Палитра цвета"); self.setModal(True); self.setFixedSize(520, 340)
        self._alpha = max(0.0, min(1.0, alpha)); self._color = QColor(base_color)
        self._build_ui(); self._sync_from_color()
    def _build_ui(self):
        root = QHBoxLayout(self)
        self.wheel = HSVWheel(self); root.addWidget(self.wheel, 1)
        side = QVBoxLayout(); root.addLayout(side, 0)
        self.preview = QLabel(); self.preview.setFixedSize(48, 48); self.preview.setStyleSheet("border:1px solid #1A1B20; border-radius:10px; background:#00FF00;"); side.addWidget(self.preview)
        side.addSpacing(6); side.addWidget(QLabel("Яркость"))
        self.sldr_value = QSlider(Qt.Horizontal); self.sldr_value.setRange(0, 100); self.sldr_value.setValue(100); side.addWidget(self.sldr_value)
        side.addWidget(QLabel("Прозрачность"))
        self.sldr_alpha = QSlider(Qt.Horizontal); self.sldr_alpha.setRange(0, 100); self.sldr_alpha.setValue(int(round(self._alpha*100))); side.addWidget(self.sldr_alpha)
        side.addSpacing(6); row = QHBoxLayout(); side.addLayout(row)
        row.addWidget(QLabel("HEX:")); self.hex_edit = QLineEdit("#00FF00"); self.hex_edit.setFixedWidth(120); row.addWidget(self.hex_edit); row.addStretch(1)
        side.addStretch(1); btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel); side.addWidget(btns)
        # signals
        self.wheel.colorChanged.connect(self._on_wheel); self.sldr_value.valueChanged.connect(self._on_v_or_a); self.sldr_alpha.valueChanged.connect(self._on_v_or_a)
        self.hex_edit.editingFinished.connect(self._on_hex); btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
    def _sync_from_color(self):
        c = QColor(self._color); h,s,v,a = c.getHsvF();
        if h < 0: h = 0.33
        self.wheel.setHSV(h, s if s>0 else 1.0, v if v>0 else 1.0); self.sldr_value.setValue(int(round(v*100))); self.sldr_alpha.setValue(int(round(self._alpha*100)))
        self.hex_edit.setText(c.name(QColor.HexRgb)); self._update_preview()
    def _compose_color(self) -> QColor:
        col = self.wheel.color(); v = self.sldr_value.value()/100.0; a = self.sldr_alpha.value()/100.0
        return QColor.fromHsvF(col.hsvHueF(), col.hsvSaturationF(), v, a)
    def _update_preview(self):
        col = self._compose_color(); self.preview.setStyleSheet(f"border:1px solid #1A1B20; border-radius:10px; background:{col.name(QColor.HexRgb)};")
    def _on_wheel(self, _):
        col = self._compose_color(); self.hex_edit.setText(col.name(QColor.HexRgb)); self._update_preview()
    def _on_v_or_a(self, _):
        col = self._compose_color(); self.hex_edit.setText(col.name(QColor.HexRgb)); self._update_preview()
    def _on_hex(self):
        txt = self.hex_edit.text().strip();
        if not txt.startswith('#'): txt = '#' + txt
        if len(txt) == 4: txt = '#' + ''.join(c*2 for c in txt[1:])
        col = QColor(txt)
        if not col.isValid(): QMessageBox.warning(self, "Цвет", "Неверный HEX"); return
        self._color = col; h,s,v,_ = col.getHsvF();
        if h < 0: h = 0.33
        self.wheel.setHSV(h, s if s>0 else 1.0, v if v>0 else 1.0); self._update_preview()
    def selected_color_hex(self) -> str: return self._compose_color().name(QColor.HexRgb)
    def selected_alpha(self) -> float:  return self._compose_color().alphaF()

# =========================== Окно-оверлей ===========================
class OverlayWindow(QWidget):
    def __init__(self, screen_geometry: QRect, settings: Settings):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.WindowTransparentForInput, True)  # click-through
        self._settings = settings
        self._pen_cache: QPen | None = None
        self._place(screen_geometry)

    def _place(self, screen_geometry: QRect):
        size = QSize(self._settings.canvas_size, self._settings.canvas_size)
        top_left = screen_geometry.center() - QPoint(size.width() // 2, size.height() // 2)
        self.setGeometry(QRect(top_left, size))

    def apply(self, s: Settings, screen_geometry: QRect | None = None):
        self._settings = s
        self._pen_cache = None
        if screen_geometry is not None:
            self._place(screen_geometry)
        self.update()

    def _pen(self, color: QColor | None = None, thickness: int | None = None) -> QPen:
        if color is None and thickness is None and self._pen_cache is not None:
            return self._pen_cache
        if color is None:
            color = QColor(self._settings.color_hex)
            color.setAlphaF(max(0.0, min(1.0, self._settings.opacity)))
        pen = QPen(color, max(1, int(round((thickness if thickness is not None else self._settings.thickness) * self._settings.scale))))
        pen.setCapStyle(Qt.FlatCap)
        if color is None and thickness is None:
            self._pen_cache = pen
        return pen

    def paintEvent(self, _):
        s = self._settings
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        rect = self.rect()
        c = rect.center() + QPoint(s.offset_x, s.offset_y)
        scale = max(0.1, min(4.0, s.scale))

        objs = s.current_objects()
        hide_base = s.scene_hide_crosshair() or len(objs) > 0

        # ---- Базовый прицел (если не скрыт сценой) ----
        if not hide_base:
            p.setPen(self._pen())
            if s.style == "Dot":
                dot_r = max(1, int(round((s.thickness + 1) * scale)))
                col = QColor(s.color_hex); col.setAlphaF(max(0.0, min(1.0, s.opacity)))
                p.setBrush(col); p.setOpacity(1.0); p.drawEllipse(c, dot_r, dot_r)
            else:
                if s.style in ("Cross", "CrossCircle"):
                    g = max(0, int(round(s.gap * scale)))
                    L = max(2, int(round(s.length * scale)))
                    p.drawLine(QPoint(c.x() - g - L, c.y()), QPoint(c.x() - g, c.y()))
                    p.drawLine(QPoint(c.x() + g, c.y()), QPoint(c.x() + g + L, c.y()))
                    p.drawLine(QPoint(c.x(), c.y() - g - L), QPoint(c.x(), c.y() - g))
                    p.drawLine(QPoint(c.x(), c.y() + g), QPoint(c.x(), c.y() + g + L))
                if s.style in ("Circle", "CrossCircle"):
                    R = max(2, int(round(s.radius * scale)))
                    p.setBrush(Qt.NoBrush); p.drawEllipse(c, R, R)

        # ---- Объекты сцены ----
        if objs:
            for obj in objs:
                otype = obj.get("type", "Circle")
                ox = int(obj.get("x", 0)); oy = int(obj.get("y", 0))
                rot = float(obj.get("rotation", 0.0))
                oscale = float(obj.get("scale", 1.0))
                size_a = int(obj.get("size_a", 40))
                size_b = int(obj.get("size_b", 30))
                thick  = int(obj.get("thickness", 2))
                fill   = bool(obj.get("fill", False))
                colhex = obj.get("color_hex", "#FF0000")
                alpha  = float(obj.get("opacity", 1.0))
                sides  = int(obj.get("sides", 5))

                col = QColor(colhex); col.setAlphaF(max(0.0, min(1.0, alpha)))

                p.save()
                p.translate(c + QPoint(ox, oy))
                p.rotate(rot)
                p.scale(max(0.1, oscale), max(0.1, oscale))
                p.setPen(self._pen(col, thick))
                p.setBrush(col if fill else Qt.NoBrush)

                if otype == "Line":
                    L = max(1, size_a)
                    p.setBrush(Qt.NoBrush)
                    p.drawLine(QPoint(-L//2, 0), QPoint(L//2, 0))

                elif otype == "Rect":
                    w = max(1, size_a); h = max(1, size_b)
                    p.drawRect(-w//2, -h//2, w, h)

                elif otype == "Circle":
                    r = max(1, size_a); p.drawEllipse(QPoint(0, 0), r, r)

                elif otype == "Cross":
                    L = max(2, size_a); G = max(0, size_b)
                    p.drawLine(QPoint(-(G//2) - L, 0), QPoint(-(G//2), 0))
                    p.drawLine(QPoint((G//2), 0), QPoint((G//2) + L, 0))
                    p.drawLine(QPoint(0, -(G//2) - L), QPoint(0, -(G//2)))
                    p.drawLine(QPoint(0, (G//2)), QPoint(0, (G//2) + L))

                elif otype == "XCross":
                    L = max(2, size_a)
                    p.drawLine(QPoint(-L, -L), QPoint(L, L))
                    p.drawLine(QPoint(-L, L), QPoint(L, -L))

                elif otype == "Triangle":
                    r = max(1, size_a)
                    poly = QPolygon()
                    for i in range(3):
                        ang = -math.pi/2 + 2*math.pi*i/3
                        poly.append(QPoint(int(math.cos(ang)*r), int(math.sin(ang)*r)))
                    p.drawPolygon(poly)

                elif otype == "NGon":
                    r = max(1, size_a); n = max(3, min(24, sides))
                    poly = QPolygon()
                    for i in range(n):
                        ang = -math.pi/2 + 2*math.pi*i/n
                        poly.append(QPoint(int(math.cos(ang)*r), int(math.sin(ang)*r)))
                    p.drawPolygon(poly)

                p.restore()


# =========================== Менеджер экранов ===========================
class OverlayManager:
    def __init__(self, app: QApplication, settings: Settings):
        self.app = app; self.settings = settings; self.overlays: List[OverlayWindow] = []
        self._create_per_screen()
    def _create_per_screen(self):
        self.overlays.clear()
        for screen in self.app.screens(): self.overlays.append(OverlayWindow(screen.geometry(), self.settings))
        self.apply(self.settings)
    def recreate_geometry(self):
        for screen, wnd in zip(self.app.screens(), self.overlays): wnd.apply(self.settings, screen.geometry())
    def show(self):
        for w in self.overlays: w.show()
    def hide(self):
        for w in self.overlays: w.hide()
    def toggle(self):
        (self.hide() if any(w.isVisible() for w in self.overlays) else self.show())
    def apply(self, s: Settings):
        for screen, w in zip(self.app.screens(), self.overlays): w.apply(s, screen.geometry())
        (self.show() if s.visible else self.hide())

# =========================== Диалог выбора типа объекта ===========================
class AddObjectDialog(QDialog):
    TYPES = [
        ("Circle",   "Круг"),
        ("Rect",     "Прямоугольник"),
        ("Line",     "Линия"),
        ("Cross",    "Крест"),
        ("XCross",   "Диагональный крест"),
        ("Triangle", "Треугольник"),
        ("NGon",     "N‑угольник"),
    ]
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить объект")
        self.setModal(True)
        self.setFixedSize(320, 360)
        lay = QVBoxLayout(self)
        self.list = QListWidget(); lay.addWidget(self.list, 1)
        for k, title in self.TYPES:
            item = QListWidgetItem(title)
            item.setData(Qt.UserRole, k)
            self.list.addItem(item)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        lay.addWidget(btns)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
    def selected_type(self) -> str:
        it = self.list.currentItem()
        return it.data(Qt.UserRole) if it else "Circle"

# =========================== Главное окно ===========================
class MainWindow(QMainWindow):
    def __init__(self, manager: OverlayManager, settings: Settings):
        super().__init__(); self.manager = manager; self.settings = settings; self.current_alpha = settings.opacity
        self._loading = False
        self.setWindowTitle("CrosshairLite-Python — настройки")
        self.setMinimumSize(QSize(780, 560))
        self.resize(QSize(960, 660))
        self._build_ui(); self._init_tray(); self._load_to_ui(settings)

    def _build_ui(self):
        tabs = QTabWidget(self); self.setCentralWidget(tabs)

        # -------- Tab: Прицел --------
        w_cross = QWidget(); tabs.addTab(w_cross, "Прицел"); v = QVBoxLayout(w_cross); v.setContentsMargins(12,12,12,12); v.setSpacing(10)

        top = QHBoxLayout(); v.addLayout(top)
        self.chk_auto = QCheckBox("Автоприменение"); self.chk_auto.setChecked(True)
        top.addWidget(QLabel("F8 — показать/скрыть")); top.addStretch(1); top.addWidget(self.chk_auto)

        box_style = QGroupBox("Базовые настройки"); v.addWidget(box_style); form = QFormLayout(box_style)
        self.cmb_style = QComboBox(); self.cmb_style.addItems(["Dot", "Cross", "Circle", "CrossCircle"]); form.addRow("Стиль", self.cmb_style)

        box_color = QGroupBox("Цвет"); v.addWidget(box_color); h = QHBoxLayout(box_color)
        self.btn_color = QPushButton("Открыть палитру…"); self.lbl_preview = QLabel(); self.lbl_preview.setFixedSize(32,32)
        self.lbl_preview.setStyleSheet("border:1px solid #1A1B20; border-radius:8px; background:#00FF00;")
        self.hex_edit = QLineEdit("#00FF00"); self.hex_edit.setFixedWidth(120)
        h.addWidget(self.btn_color); h.addSpacing(8); h.addWidget(self.lbl_preview); h.addSpacing(8); h.addWidget(QLabel("HEX:")); h.addWidget(self.hex_edit); h.addStretch(1)

        box_sizes = QGroupBox("Размеры"); v.addWidget(box_sizes); g = QFormLayout(box_sizes)
        self.spin_thick = self._spin(1, 20, 2); self.spin_len = self._spin(2, 200, 24); self.spin_gap = self._spin(0, 100, 6); self.spin_rad = self._spin(2,200,18); self.spin_scale = self._spin_double(0.5,2.0,1.0,0.05)
        g.addRow("Толщина", self._pair(self._slider(1,20,2), self.spin_thick))
        g.addRow("Длина луча", self._pair(self._slider(2,200,24), self.spin_len))
        g.addRow("Разрыв", self._pair(self._slider(0,100,6), self.spin_gap))
        g.addRow("Радиус круга", self._pair(self._slider(2,200,18), self.spin_rad))
        g.addRow(QLabel("Scale %"), self._pair(self._slider(50,200,100), self.spin_scale, is_percent=True))

        box_offsets = QGroupBox("Позиция"); v.addWidget(box_offsets); gh = QHBoxLayout(box_offsets)
        self.offx = self._spin(-2000,2000,0); self.offy = self._spin(-2000,2000,0)
        gh.addWidget(QLabel("X:")); gh.addWidget(self.offx); gh.addSpacing(16); gh.addWidget(QLabel("Y:")); gh.addWidget(self.offy); gh.addStretch(1)

        row = QHBoxLayout(); v.addLayout(row)
        self.btn_toggle = QPushButton("Показать/Скрыть"); self.btn_save = QPushButton("Сохранить настройки")
        row.addStretch(1); row.addWidget(self.btn_toggle); row.addWidget(self.btn_save)

        # -------- Tab: Сцены --------
        w_scn = QWidget(); tabs.addTab(w_scn, "Сцены"); vs = QVBoxLayout(w_scn); vs.setContentsMargins(12,12,12,12); vs.setSpacing(10)

        # пресеты
        box_sc = QGroupBox("Пресеты сцены"); vs.addWidget(box_sc)
        grid = QGridLayout(box_sc)
        self.cmb_scene = QComboBox()
        self.chk_scene_hide = QCheckBox()
        lbl_scene_hide = QLabel("Скрывать прицел в этой сцене"); lbl_scene_hide.setWordWrap(True)
        self.wrap_scene_hide = QWidget(); _hl = QHBoxLayout(self.wrap_scene_hide); _hl.setContentsMargins(0,0,0,0); _hl.setSpacing(6)
        _hl.addWidget(self.chk_scene_hide, 0, Qt.AlignTop); _hl.addWidget(lbl_scene_hide, 1)
        self.btn_scene_new = QPushButton("Создать новую сцену…")
        self.ed_scenename = QLineEdit(); self.ed_scenename.setPlaceholderText("Имя сцены для «Сохранить как…»")
        self.btn_scene_save = QPushButton("Сохранить/Обновить")
        self.btn_scene_new_as  = QPushButton("Сохранить как…")
        self.btn_scene_del  = QPushButton("Удалить")
        self.btn_scene_load = QPushButton("Загрузить")

        grid.addWidget(QLabel("Текущая:"), 0, 0)
        grid.addWidget(self.cmb_scene, 0, 1, 1, 2)
        grid.addWidget(self.wrap_scene_hide, 0, 3, 1, 2)
        grid.addWidget(self.btn_scene_new, 0, 5)

        grid.addWidget(QLabel("Имя:"), 1, 0)
        grid.addWidget(self.ed_scenename, 1, 1, 1, 2)
        grid.addWidget(self.btn_scene_save, 1, 3)
        grid.addWidget(self.btn_scene_new_as, 1, 4)
        grid.addWidget(self.btn_scene_del, 1, 5)
        grid.addWidget(self.btn_scene_load, 1, 6)

        for b in (self.btn_scene_new, self.btn_scene_save, self.btn_scene_new_as, self.btn_scene_del, self.btn_scene_load):
            b.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)

        # редактор объектов
        box_ed = QGroupBox("Редактор объектов"); vs.addWidget(box_ed)
        edh = QHBoxLayout(box_ed)
        self.obj_list = QListWidget(); self.obj_list.setMinimumWidth(240); edh.addWidget(self.obj_list, 0)
        prop = QGroupBox("Свойства объекта"); edh.addWidget(prop, 1)
        fp = QFormLayout(prop)
        self.obj_type = QLabel("—"); fp.addRow("Тип", self.obj_type)
        self.obj_x = self._spin(-3000, 3000, 0); fp.addRow("X", self.obj_x)
        self.obj_y = self._spin(-3000, 3000, 0); fp.addRow("Y", self.obj_y)
        self.obj_rot = QDoubleSpinBox(); self.obj_rot.setRange(-360.0, 360.0); self.obj_rot.setSingleStep(1.0); self.obj_rot.setDecimals(1); fp.addRow("Поворот°", self.obj_rot)
        self.obj_scale = self._spin_double(0.1, 4.0, 1.0, 0.05); fp.addRow("Scale", self.obj_scale)
        self.obj_a = self._spin(1, 2000, 40); fp.addRow("Размер A", self.obj_a)
        self.obj_b = self._spin(0, 2000, 30); fp.addRow("Размер B/Gap", self.obj_b)
        self.obj_sides = self._spin(3, 24, 5); fp.addRow("Стороны (для N‑уг.)", self.obj_sides)
        self.obj_th = self._spin(1, 50, 2); fp.addRow("Толщина", self.obj_th)
        self.obj_fill = QCheckBox(); fp.addRow("Заливка", self.obj_fill)
        colorRowLayout = QHBoxLayout()
        self.obj_color_btn = QPushButton("Цвет…"); self.obj_color_prev = QLabel(); self.obj_color_prev.setFixedSize(24,24)
        self.obj_color_prev.setStyleSheet("border:1px solid #1A1B20; border-radius:6px; background:#FF0000;")
        self.obj_hex = QLineEdit("#FF0000"); self.obj_hex.setFixedWidth(110)
        colorRowLayout.addWidget(self.obj_color_btn); colorRowLayout.addWidget(self.obj_color_prev); colorRowLayout.addWidget(QLabel("HEX:")); colorRowLayout.addWidget(self.obj_hex); colorRow = QWidget(); colorRow.setLayout(colorRowLayout)
        fp.addRow("Цвет", colorRow)
        self.obj_alpha = self._spin_double(0.0, 1.0, 1.0, 0.05); fp.addRow("Прозрачн.", self.obj_alpha)

        btnrow = QHBoxLayout(); vs.addLayout(btnrow)
        self.btn_add_object = QPushButton("Добавить объект…")
        self.btn_dup        = QPushButton("Дублировать")
        self.btn_del        = QPushButton("Удалить")
        self.btn_up         = QPushButton("Вверх")
        self.btn_down       = QPushButton("Вниз")
        for b in (self.btn_add_object, self.btn_dup, self.btn_del, self.btn_up, self.btn_down): btnrow.addWidget(b)

        # -------- Tab: Вид --------
        w_view = QWidget(); tabs.addTab(w_view, "Вид"); vv = QVBoxLayout(w_view); vv.setContentsMargins(12,12,12,12); vv.setSpacing(10)
        box_view = QGroupBox("Окно-оверлея"); vv.addWidget(box_view); fv = QFormLayout(box_view)
        self.spin_canvas = self._spin(300, 1400, self.settings.canvas_size); fv.addRow("Canvas Size", self._pair(self._slider(300,1400,self.settings.canvas_size), self.spin_canvas))
        vv.addStretch(1)

        # Сигналы (автоприменение)
        for w in [self.cmb_style, self.hex_edit, self.spin_thick, self.spin_len, self.spin_gap, self.spin_rad, self.spin_scale, self.offx, self.offy]:
            if isinstance(w, (QComboBox,)):
                w.currentIndexChanged.connect(self._auto_apply)
            elif isinstance(w, (QLineEdit,)):
                w.editingFinished.connect(self._auto_apply)
            else:  # spin
                w.valueChanged.connect(self._auto_apply)
        self.chk_auto.toggled.connect(self._on_auto_toggle)
        self.btn_color.clicked.connect(self._open_palette_dialog)
        self.btn_save.clicked.connect(self._save)
        self.btn_toggle.clicked.connect(self._toggle)

        # сцены — пресеты
        self.btn_scene_new.clicked.connect(self._scene_create_new_dialog)
        self.btn_scene_save.clicked.connect(self._scene_save_overwrite)
        self.btn_scene_new_as.clicked.connect(self._scene_save_as)
        self.btn_scene_del.clicked.connect(self._scene_delete)
        self.btn_scene_load.clicked.connect(self._scene_load)
        self.cmb_scene.currentTextChanged.connect(self._on_scene_combo)
        self.chk_scene_hide.toggled.connect(self._on_scene_hide_toggle)

        # сцены — объекты
        self.obj_list.currentRowChanged.connect(self._on_obj_select)
        for w in [self.obj_x, self.obj_y]: w.valueChanged.connect(self._obj_changed)
        for w in [self.obj_rot, self.obj_scale, self.obj_a, self.obj_b, self.obj_th, self.obj_alpha, self.obj_sides]: w.valueChanged.connect(self._obj_changed)
        self.obj_fill.toggled.connect(self._obj_changed)
        self.obj_color_btn.clicked.connect(self._obj_color_dialog)
        self.obj_hex.editingFinished.connect(self._obj_hex_applied)

        self.btn_add_object.clicked.connect(self._obj_add_dialog)
        self.btn_del.clicked.connect(self._obj_delete)
        self.btn_dup.clicked.connect(self._obj_duplicate)
        self.btn_up.clicked.connect(lambda: self._obj_reorder(-1))
        self.btn_down.clicked.connect(lambda: self._obj_reorder(1))

        # вид
        self.spin_canvas.valueChanged.connect(self._on_canvas_size)

    # --- Хелперы ---
    def _slider(self, a, b, v): s = QSlider(Qt.Horizontal); s.setRange(a,b); s.setValue(v); return s
    def _spin(self, a, b, v): sp = QSpinBox(); sp.setRange(a,b); sp.setValue(v); return sp
    def _spin_double(self, a, b, v, step=0.1): sp = QDoubleSpinBox(); sp.setDecimals(2); sp.setSingleStep(step); sp.setRange(a,b); sp.setValue(v); return sp
    def _pair(self, slider: QSlider, spin, is_percent=False):
        w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(0,0,0,0); h.addWidget(slider,1); h.addSpacing(8); h.addWidget(spin)
        if is_percent:
            def on_s(v): spin.setValue(v/100.0)
            def on_p(val): slider.setValue(int(round(val*100)))
            slider.valueChanged.connect(on_s); spin.valueChanged.connect(on_p)
        else:
            slider.valueChanged.connect(spin.setValue); spin.valueChanged.connect(slider.setValue)
        return w

    # ----- Трэй -----
    def _make_tray_icon(self) -> QIcon:
        px = QPixmap(16,16); px.fill(Qt.transparent); p = QPainter(px); p.setRenderHint(QPainter.Antialiasing, True)
        p.setBrush(QColor("#00FF00")); p.setPen(Qt.NoPen); p.drawEllipse(px.rect().center(), 6, 6); p.end(); return QIcon(px)
    def _init_tray(self):
        self.tray = QSystemTrayIcon(self); icon = self._make_tray_icon()
        if icon.isNull(): icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray.setIcon(icon); m = QMenu();
        act_show = QAction("Настройки", self); act_show.triggered.connect(self.showNormal); m.addAction(act_show)
        act_toggle = QAction("Показать/Скрыть (F8)", self); act_toggle.triggered.connect(self._toggle); m.addAction(act_toggle)
        act_exit = QAction("Выход", self); act_exit.triggered.connect(QApplication.instance().quit); m.addAction(act_exit)
        self.tray.setContextMenu(m); self.tray.setVisible(True)

    # ----- Settings <-> UI -----
    def _load_to_ui(self, s: Settings):
        self._loading = True
        self.chk_auto.setChecked(bool(s.auto_apply))
        self.cmb_style.setCurrentText(s.style if s.style in ("Dot","Cross","Circle","CrossCircle") else "Cross")
        self.hex_edit.setText(s.color_hex); self.current_alpha = s.opacity; self._set_preview_color(QColor(s.color_hex))
        self.spin_thick.setValue(s.thickness); self.spin_len.setValue(s.length); self.spin_gap.setValue(s.gap); self.spin_rad.setValue(s.radius)
        self.spin_scale.setValue(s.scale); self.offx.setValue(s.offset_x); self.offy.setValue(s.offset_y)
        self.spin_canvas.setValue(s.canvas_size)
        self._refresh_scene_combo()
        self._load_scene_objects_to_editor()
        self.chk_scene_hide.setChecked(self.settings.scene_hide_crosshair())
        self._loading = False

    def _read_from_ui(self) -> Settings:
        s = self.settings
        s.auto_apply = self.chk_auto.isChecked()
        s.style = self.cmb_style.currentText(); s.color_hex = self._sanitize_hex(self.hex_edit.text()); s.opacity = float(self.current_alpha)
        s.thickness = int(self.spin_thick.value()); s.length = int(self.spin_len.value()); s.gap = int(self.spin_gap.value()); s.radius = int(self.spin_rad.value())
        s.scale = float(self.spin_scale.value()); s.offset_x = int(self.offx.value()); s.offset_y = int(self.offy.value()); s.canvas_size = int(self.spin_canvas.value())
        s.set_current_objects(self._collect_objects_from_editor())
        return s

    def _sanitize_hex(self, txt: str) -> str:
        t = txt.strip();  
        if not t.startswith('#'): t = '#' + t
        if len(t) == 4: t = '#' + ''.join(c*2 for c in t[1:])
        return t[:7]

    # ----- Палитра для прицела -----
    def _open_palette_dialog(self):
        base = QColor(self._sanitize_hex(self.hex_edit.text()));  
        if not base.isValid(): base = QColor(self.settings.color_hex)
        dlg = ColorDialog(base, self.current_alpha, self)
        if dlg.exec() == QDialog.Accepted:
            self.hex_edit.setText(dlg.selected_color_hex()); self.current_alpha = dlg.selected_alpha(); self._set_preview_color(QColor(self.hex_edit.text()))
            self._auto_apply()

    def _set_preview_color(self, col: QColor):
        self.lbl_preview.setStyleSheet(f"border:1px solid #1A1B20; border-radius:8px; background:{col.name(QColor.HexRgb)};")

    # ----- Сцены: пресеты -----
    def _refresh_scene_combo(self):
        self.cmb_scene.blockSignals(True); self.cmb_scene.clear(); names = sorted(self.settings.scenes.keys())
        if not names: self.settings.scenes["Default"] = self.settings.scene_from_self(); names = ["Default"]
        self.cmb_scene.addItems(names)
        idx = self.cmb_scene.findText(self.settings.active_scene); self.cmb_scene.setCurrentIndex(max(0, idx))
        self.cmb_scene.blockSignals(False)

    def _scene_create_new_dialog(self):
        name, ok = QInputDialog.getText(self, "Новая сцена", "Название сцены:")
        if not ok or not name.strip():
            return
        name = name.strip()
        self.settings.scenes[name] = {
            "style": self.settings.style,
            "color_hex": self.settings.color_hex,
            "opacity": self.settings.opacity,
            "thickness": self.settings.thickness,
            "length": self.settings.length,
            "gap": self.settings.gap,
            "radius": self.settings.radius,
            "offset_x": self.settings.offset_x,
            "offset_y": self.settings.offset_y,
            "scale": self.settings.scale,
            "objects": [],
            "hide_crosshair": True,
        }
        self.settings.active_scene = name
        self.settings.save()
        self._refresh_scene_combo()
        self._load_scene_objects_to_editor()
        self.chk_scene_hide.setChecked(True)
        self._auto_apply()

    def _scene_save_overwrite(self):
        name = self.cmb_scene.currentText() or "Default"
        self._apply_from_ui()
        sc = self.settings.scene_from_self()
        sc["hide_crosshair"] = self.settings.scenes.get(name, {}).get("hide_crosshair", False)
        self.settings.scenes[name] = sc
        self.settings.active_scene = name
        self.settings.save()
        self._refresh_scene_combo()

    def _scene_save_as(self):
        name = self.ed_scenename.text().strip()
        if not name:
            QMessageBox.information(self, "Сцена", "Введите имя для 'Сохранить как…'")
            return
        self._apply_from_ui()
        sc = self.settings.scene_from_self()
        sc["hide_crosshair"] = self.chk_scene_hide.isChecked()
        self.settings.scenes[name] = sc
        self.settings.active_scene = name
        self.settings.save(); self._refresh_scene_combo(); self.cmb_scene.setCurrentText(name)

    def _scene_delete(self):
        name = self.cmb_scene.currentText()
        if name and name in self.settings.scenes:
            del self.settings.scenes[name]
            if not self.settings.scenes:
                self.settings.scenes["Default"] = self.settings.scene_from_self(); self.settings.active_scene = "Default"
            else:
                self.settings.active_scene = next(iter(self.settings.scenes.keys()))
            self.settings.save(); self._refresh_scene_combo(); self._load_scene_objects_to_editor(); self._auto_apply()

    def _scene_load(self):
        name = self.cmb_scene.currentText()
        if name in self.settings.scenes:
            self.settings.apply_scene_to_self(name)
            self._load_to_ui(self.settings)
            self.manager.apply(self.settings)
            self.settings.save()

    def _on_scene_combo(self, name: str):
        self.ed_scenename.setText(name)
        self.chk_scene_hide.setChecked(self.settings.scenes.get(name, {}).get("hide_crosshair", False))

    def _on_scene_hide_toggle(self, val: bool):
        name = self.cmb_scene.currentText()
        sc = self.settings.scenes.setdefault(name, {})
        sc["hide_crosshair"] = bool(val)
        self._auto_apply()

    # ----- Редактор объектов сцены -----
    def _load_scene_objects_to_editor(self):
        self.obj_list.clear()
        for i, obj in enumerate(self.settings.current_objects()):
            item = QListWidgetItem(self._obj_title(obj, i))
            item.setData(Qt.UserRole, obj)
            self.obj_list.addItem(item)
        if self.obj_list.count() > 0:
            self.obj_list.setCurrentRow(0)
        else:
            self._clear_obj_props()

    def _collect_objects_from_editor(self) -> List[dict]:
        objs: List[dict] = []
        for i in range(self.obj_list.count()):
            obj = self.obj_list.item(i).data(Qt.UserRole)
            if isinstance(obj, dict):
                objs.append(obj)
        return objs

    def _obj_title(self, obj: dict, idx: int) -> str:
        t = obj.get("type", "Circle")
        return f"{idx+1}. {t}"

    def _clear_obj_props(self):
        self.obj_type.setText("—")
        for w in [self.obj_x, self.obj_y]: w.setValue(0)
        for w in [self.obj_rot]: w.setValue(0.0)
        for w in [self.obj_scale]: w.setValue(1.0)
        self.obj_a.setValue(40); self.obj_b.setValue(30); self.obj_th.setValue(2)
        self.obj_fill.setChecked(False)
        self.obj_hex.setText("#FF0000"); self.obj_alpha.setValue(1.0)
        self.obj_color_prev.setStyleSheet("border:1px solid #1A1B20; border-radius:6px; background:#FF0000;")
        self.obj_sides.setValue(5)

    def _on_obj_select(self, row: int):
        if row < 0:
            self._clear_obj_props(); return
        item = self.obj_list.item(row)
        obj = item.data(Qt.UserRole)
        if not isinstance(obj, dict):
            obj = {"type":"Circle", "x":0, "y":0, "rotation":0.0, "scale":1.0, "size_a":40, "size_b":30, "thickness":2, "fill":False, "color_hex":"#FF0000", "opacity":1.0, "sides":5}
            item.setData(Qt.UserRole, obj)
        self.obj_type.setText(obj.get("type", "Circle"))
        self.obj_x.setValue(int(obj.get("x", 0))); self.obj_y.setValue(int(obj.get("y", 0)))
        self.obj_rot.setValue(float(obj.get("rotation", 0.0)))
        self.obj_scale.setValue(float(obj.get("scale", 1.0)))
        self.obj_a.setValue(int(obj.get("size_a", 40))); self.obj_b.setValue(int(obj.get("size_b", 30)))
        self.obj_th.setValue(int(obj.get("thickness", 2)))
        self.obj_fill.setChecked(bool(obj.get("fill", False)))
        self.obj_hex.setText(obj.get("color_hex", "#FF0000"))
        self.obj_alpha.setValue(float(obj.get("opacity", 1.0)))
        self.obj_sides.setValue(int(obj.get("sides", 5)))
        self.obj_color_prev.setStyleSheet(f"border:1px solid #1A1B20; border-radius:6px; background:{self.obj_hex.text()};")

    def _push_obj_form_to_item(self):
        row = self.obj_list.currentRow()
        if row < 0: return
        item = self.obj_list.item(row)
        obj = item.data(Qt.UserRole) or {}
        obj.update({
            "type": self.obj_type.text() or "Circle",
            "x": int(self.obj_x.value()),
            "y": int(self.obj_y.value()),
            "rotation": float(self.obj_rot.value()),
            "scale": float(self.obj_scale.value()),
            "size_a": int(self.obj_a.value()),
            "size_b": int(self.obj_b.value()),
            "thickness": int(self.obj_th.value()),
            "fill": bool(self.obj_fill.isChecked()),
            "color_hex": self._sanitize_hex(self.obj_hex.text()),
            "opacity": float(self.obj_alpha.value()),
            "sides": int(self.obj_sides.value()),
        })
        item.setData(Qt.UserRole, obj)
        item.setText(self._obj_title(obj, row))

    def _obj_changed(self, *_):
        self._push_obj_form_to_item(); self._auto_apply()

    def _obj_color_dialog(self):
        base = QColor(self._sanitize_hex(self.obj_hex.text()))
        if not base.isValid(): base = QColor("#FF0000")
        dlg = ColorDialog(base, float(self.obj_alpha.value()), self)
        if dlg.exec() == QDialog.Accepted:
            self.obj_hex.setText(dlg.selected_color_hex())
            self.obj_alpha.setValue(dlg.selected_alpha())
            self.obj_color_prev.setStyleSheet(f"border:1px solid #1A1B20; border-radius:6px; background:{self.obj_hex.text()};")
            self._obj_changed()

    def _obj_hex_applied(self):
        txt = self._sanitize_hex(self.obj_hex.text()); col = QColor(txt)
        if not col.isValid(): QMessageBox.warning(self, "Цвет", "Неверный HEX-цвет"); return
        self.obj_hex.setText(txt)
        self.obj_color_prev.setStyleSheet(f"border:1px solid #1A1B20; border-radius:6px; background:{txt};")
        self._obj_changed()

    def _obj_add_dialog(self):
        dlg = AddObjectDialog(self)
        if dlg.exec() == QDialog.Accepted:
            typ = dlg.selected_type(); self._obj_add(typ)

    def _obj_add(self, typ: str):
        defaults = {"Circle": (40, 0), "Rect": (60, 40), "Line": (120, 0), "Cross": (40, 8), "XCross": (40, 0), "Triangle": (40, 0), "NGon": (40, 0)}
        a, b = defaults.get(typ, (40, 0))
        obj = {"type": typ, "x":0, "y":0, "rotation":0.0, "scale":1.0, "size_a":a, "size_b":b, "thickness":2, "fill": False, "color_hex":"#FF0000", "opacity":1.0, "sides":5}
        item = QListWidgetItem(self._obj_title(obj, self.obj_list.count()))
        item.setData(Qt.UserRole, obj)
        self.obj_list.addItem(item)
        self.obj_list.setCurrentItem(item)
        self._auto_apply()

    def _obj_delete(self):
        row = self.obj_list.currentRow()
        if row < 0: return
        self.obj_list.takeItem(row)
        if self.obj_list.count(): self.obj_list.setCurrentRow(min(row, self.obj_list.count()-1))
        self._auto_apply()

    def _obj_duplicate(self):
        row = self.obj_list.currentRow()
        if row < 0: return
        src = self.obj_list.item(row).data(Qt.UserRole)
        if not isinstance(src, dict): return
        dup = dict(src)
        item = QListWidgetItem(self._obj_title(dup, self.obj_list.count()))
        item.setData(Qt.UserRole, dup)
        self.obj_list.insertItem(row+1, item)
        self.obj_list.setCurrentItem(item)
        self._auto_apply()

    def _obj_reorder(self, delta: int):
        row = self.obj_list.currentRow()
        if row < 0: return
        new_row = max(0, min(self.obj_list.count()-1, row + delta))
        if new_row == row: return
        item = self.obj_list.takeItem(row)
        self.obj_list.insertItem(new_row, item)
        self.obj_list.setCurrentItem(item)
        self._auto_apply()

    # ----- Прочее -----
    def _apply_from_ui(self):
        self.settings = self._read_from_ui(); self.manager.apply(self.settings)

    def _auto_apply(self):
        if self._loading: return
        if self.chk_auto.isChecked():
            QTimer.singleShot(0, self._apply_from_ui)

    def _on_auto_toggle(self, checked: bool):
        self.settings.auto_apply = checked
        if checked:
            self._auto_apply()

    def _save(self):
        self._apply_from_ui(); self.settings.save()

    def _toggle(self): self.manager.toggle()

    def _on_canvas_size(self):
        self.settings.canvas_size = int(self.spin_canvas.value())
        self.manager.recreate_geometry()
        self.settings.save()

# =========================== Горячая клавиша ===========================
def start_global_hotkey(toggle_cb):
    try:
        import keyboard  # type: ignore
        keyboard.add_hotkey('f8', lambda: QTimer.singleShot(0, toggle_cb)); return True
    except Exception:
        return False

# =========================== main ===========================
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_QSS)
    settings = Settings.load(); manager = OverlayManager(app, settings)
    wnd = MainWindow(manager, settings); wnd.show()
    start_global_hotkey(manager.toggle)
    (manager.show() if settings.visible else manager.hide())
    sys.exit(app.exec())

if __name__ == "__main__":
    if sys.platform != "win32": print("⚠️ Оптимизировано под Windows. На других ОС click-through может отличаться.")
    main()
