from __future__ import annotations
import json, os, sys, math, uuid, hashlib, ctypes, ssl
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Tuple, Optional

def app_base_dir() -> str:
    if sys.platform.startswith('win'):
        root = os.environ.get('APPDATA') or os.path.expanduser('~')
        d = os.path.join(root, 'CrosshairLite')
    else:
        d = os.path.join(os.path.expanduser('~'), '.crosshairlite')
    os.makedirs(d, exist_ok=True)
    return d

def cache_dir() -> str:
    d = os.path.join(app_base_dir(), 'Cache')
    os.makedirs(d, exist_ok=True)
    return d

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CTX = ssl.create_default_context()

# ------------------ Supabase ------------------
SUPABASE_URL = "https://sglnqcgehrkriusuohrh.supabase.co"
SUPABASE_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNnbG5xY2dlaHJrcml1c3VvaHJoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY0NTAzMTAsImV4cCI6MjA3MjAyNjMxMH0.Q9XT_QPn8HSN_HFm0t9GQNDsqBIE4iupomxQ5Fx4gMk"
SUPABASE_STORAGE_BUCKET = "community"
REST    = SUPABASE_URL + "/rest/v1"
STORAGE = SUPABASE_URL + "/storage/v1/object"

# ------------------ Тема ------------------
DARK_QSS = """
* { color:#EEF0F3; font-size:15px; }
QMainWindow, QWidget { background:#0B0C0F; }
QLabel { color:#CBD2DC; }

QGroupBox { border:1px solid #232631; border-radius:12px; margin-top:12px; }
QGroupBox::title { subcontrol-origin: margin; left:12px; padding:2px 8px; color:#AAB2BE; font-weight:600; }

QPushButton, QToolButton {
  background:#171a22; border:1px solid #2b2f3a; border-radius:10px;
  padding:8px 12px; color:#F2F4F8; font-weight:600;
}
QPushButton:hover, QToolButton:hover { background:#1d2230; }
QPushButton:pressed, QToolButton:pressed { background:#121620; }

QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox {
  background:#121620; border:1px solid #2b2f3a; border-radius:10px;
  padding:8px 12px; min-height:34px; color:#F2F4F8;
  selection-color:#0B0C0F; selection-background-color:#5AA9FF;
}
QAbstractSpinBox { padding-right:32px; color:#F2F4F8; }
QAbstractSpinBox:disabled, QLineEdit:disabled, QComboBox:disabled {
  color:#8A93A2; background:#0F1218; border-color:#252834;
}

QListWidget, QListView, QTreeView {
  background:#121620; color:#F2F4F8; border:1px solid #2b2f3a; border-radius:10px;
  font-size:14px;
}
QListWidget::item:selected, QListView::item:selected { background:#1d2230; color:#F2F4F8; }

QSlider::groove:horizontal { height:8px; background:#1f2430; border-radius:4px; }
QSlider::handle:horizontal { width:16px; background:#5AA9FF; border-radius:8px; margin:-6px 0; }

QMenu { background:#0B0C0F; border:1px solid #232631; border-radius:12px; padding:6px; }
QToolTip { background:#121620; color:#F2F4F8; border:1px solid #2b2f3a; border-radius:8px; }

QWidget#TitleBar { background:#0B0C0F; border:1px solid #232631; border-radius:14px; padding:6px 10px; }
QToolButton#winbtn { width:18px; height:18px; border-radius:9px; border:1px solid #3a3f4d; background:#232737; font-weight:bold; color:#E6E6E6; }
QToolButton#winbtn:hover { background:#2A3042; }
QToolButton#winbtn[role="close"] { background:#4a2730; }
QToolButton#winbtn[role="close"]:hover { background:#5c2f3a; }

QTabWidget::pane { border:1px solid #232631; border-radius:12px; top:-1px; }
QTabBar::tab {
  background:#121620; border:1px solid #2b2f3a; padding:6px 12px;
  border-top-left-radius:12px; border-top-right-radius:12px; margin-right:4px; color:#F2F4F8;
  min-width:84px; min-height:28px;
}
QTabBar::tab:selected { background:#1a2030; }
QTabBar::tab:hover { background:#1d2436; }

/* Компактная вкладка "Прицел" */
QWidget#CrossTab QLineEdit,
QWidget#CrossTab QDoubleSpinBox,
QWidget#CrossTab QSpinBox,
QWidget#CrossTab QComboBox {
  min-height:28px; font-size:13px;
}

/* Читаемая вкладка "Редактор" */
QWidget#EditorTab QLineEdit,
QWidget#EditorTab QDoubleSpinBox,
QWidget#EditorTab QSpinBox,
QWidget#EditorTab QComboBox {
  min-height:34px; font-size:14px;
}
"""

# ------------------ I18N ------------------
STRINGS = {
    'en': {'tab_crosshair':'Crosshair','tab_scenes':'Scenes','editor':'Editor','lang':'Language',
           'toggle':'Show/Hide','save':'Save','base_settings':'Basic settings','style':'Style','color':'Color',
           'sizes':'Sizes','thickness':'Thickness','ray_length':'Ray length','gap':'Gap','radius':'Circle radius',
           'scale_pct':'Scale %','position':'Position','x':'X:','y':'Y:','hint_toggle':'F8 — show/hide',
           'tab_view':'View','overlay':'Overlay window','canvas_size':'Canvas Size',
           'scenes_presets':'Scene presets','current':'Current:','create_scene':'Create scene…','delete':'Delete',
           'fs_editor':'Open editor','hide_crosshair':'Hide base crosshair in this scene',
           'add_object':'Add object','duplicate':'Duplicate','cut':'Cut out (Negate)','fill':'Fill',
           'rot':'Rotation°','alpha':'Opacity','publish':'Publish','community':'Community','refresh':'Refresh',
           'community_search':'Search…','import':'Import'},
    'ru': {'tab_crosshair':'Прицел','tab_scenes':'Сцены','editor':'Редактор','lang':'Язык',
           'toggle':'Показать/Скрыть','save':'Сохранить','base_settings':'Базовые настройки','style':'Стиль','color':'Цвет',
           'sizes':'Размеры','thickness':'Толщина','ray_length':'Длина луча','gap':'Разрыв','radius':'Радиус круга',
           'scale_pct':'Масштаб %','position':'Позиция','x':'X:','y':'Y:','hint_toggle':'F8 — показать/скрыть',
           'tab_view':'Вид','overlay':'Окно-оверлей','canvas_size':'Размер холста',
           'scenes_presets':'Пресеты сцены','current':'Текущая:','create_scene':'Создать сцену…','delete':'Удалить',
           'fs_editor':'Открыть редактор','hide_crosshair':'Скрывать базовый прицел в этой сцене',
           'add_object':'Добавить объект','duplicate':'Дублировать','cut':'Вырезать (Negate)','fill':'Заливка',
           'rot':'Поворот°','alpha':'Прозрачность','publish':'Опубликовать','community':'Сообщество',
           'refresh':'Обновить','community_search':'Поиск…','import':'Импорт'}
}

# ------------------ Settings ------------------
@dataclass
class Settings:
    style: str = "Cross"
    color_hex: str = "#FF0000"
    opacity: float = 1.0
    thickness: int = 2
    length: int = 24
    gap: int = 6
    radius: int = 18
    offset_x: int = 0
    offset_y: int = 0
    scale: float = 1.0  # фикс 1.0

    canvas_size: int = 600
    visible: bool = True
    lang: str = 'ru'

    scenes: Dict[str, dict] = field(default_factory=dict)
    active_scene: str = "Default"

    # Недавно выбранные цвета (для палитр)
    recent_colors: List[str] = field(default_factory=list)

    @staticmethod
    def path() -> str:
        return os.path.join(app_base_dir(), "settings.json")

    @classmethod
    def load(cls) -> "Settings":
        try:
            with open(cls.path(), "r", encoding="utf-8") as f:
                raw = json.load(f)
            s = cls(**{k: v for k, v in raw.items() if k in cls.__dataclass_fields__})
            if not s.scenes:
                s.scenes["Default"] = s.scene_from_self()
            if s.active_scene not in s.scenes:
                s.active_scene = next(iter(s.scenes))
            if s.lang not in STRINGS:
                s.lang = 'en'
            if not isinstance(s.recent_colors, list):
                s.recent_colors = []
            return s
        except Exception:
            s = cls()
            s.scenes["Default"] = s.scene_from_self()
            return s

    def save(self) -> None:
        with open(self.path(), "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)

    def t(self, key: str) -> str:
        return STRINGS.get(self.lang, STRINGS['en']).get(key, key)

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
        d = self.scenes.get(name, {})
        if not d:
            return
        self.style = d.get("style", self.style)
        self.color_hex = d.get("color_hex", self.color_hex)
        self.opacity = float(d.get("opacity", self.opacity))
        self.thickness = int(d.get("thickness", self.thickness))
        self.length = int(d.get("length", self.length))
        self.gap = int(d.get("gap", self.gap))
        self.radius = int(d.get("radius", self.radius))
        self.offset_x = int(d.get("offset_x", self.offset_x))
        self.offset_y = int(d.get("offset_y", self.offset_y))
        self.scale = float(d.get("scale", self.scale))
        d.setdefault("objects", [])
        d.setdefault("hide_crosshair", False if name == "Default" else True)
        self.scenes[name] = d
        self.active_scene = name

    def current_objects(self) -> List[dict]:
        return list(self.scenes.get(self.active_scene, {}).get("objects", []))

    def set_current_objects(self, objs: List[dict]):
        sc = self.scenes.setdefault(self.active_scene, {})
        sc["objects"] = objs

    def scene_hide_crosshair(self) -> bool:
        return bool(self.scenes.get(self.active_scene, {}).get("hide_crosshair", False))

# ------------------ Qt импорты ------------------
from PySide6.QtCore import (
    Qt, QPointF, QRectF, QRect, QSize, QTimer, QLineF, QByteArray, QBuffer, QAbstractNativeEventFilter, QProcess
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QPolygon, QAction, QIcon, QPixmap, QCursor
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QLineEdit,
    QPushButton, QComboBox, QSystemTrayIcon, QMenu, QDoubleSpinBox, QSpinBox, QStyle, QTabWidget,
    QGroupBox, QFormLayout, QCheckBox, QListWidget, QListWidgetItem, QSizeGrip, QGridLayout,
    QToolButton, QScrollArea, QFrame, QMessageBox, QDialog, QTextEdit, QSizePolicy, QColorDialog
)
import urllib.request, urllib.error

# ------------------ Центрирование линий ------------------
def _snap_center_for_pen(center: QPointF, pen_w: int) -> QPointF:
    if pen_w % 2 == 1:
        return QPointF(center.x() + 0.5, center.y() + 0.5)
    return center

# ------------------ Рисовальщик объектов ------------------
class ObjectPainter:
    @staticmethod
    def draw_object(p: QPainter, obj: dict, origin: QPointF, view_scale: float = 1.0, erase_preview: Optional[QColor]=None):
        t = obj.get("type", "Circle")
        ox = float(obj.get("x", 0)); oy = float(obj.get("y", 0))
        rot = float(obj.get("rotation", 0.0))
        sc  = max(0.1, float(obj.get("scale", 1.0)) * view_scale)
        a   = float(obj.get("size_a", 40))
        b   = float(obj.get("size_b", 30))
        thick  = max(1.0, float(obj.get("thickness", 2)))
        fill   = bool(obj.get("fill", False))
        colhex = obj.get("color_hex", "#FF0000")
        alpha  = float(obj.get("opacity", 1.0))
        sides  = int(obj.get("sides", 5))
        is_cut = bool(obj.get("cut", False))

        col = QColor(colhex); col.setAlphaF(max(0.0, min(1.0, alpha)))
        pen_w = max(1, int(round(thick * sc)))

        p.save()
        p.translate(origin + QPointF(ox, oy))
        p.scale(sc, sc)
        p.rotate(rot)

        if is_cut:
            p.setCompositionMode(QPainter.CompositionMode_Clear if erase_preview is None else p.compositionMode())
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255,255,255) if erase_preview is None else erase_preview)
        else:
            p.setPen(QPen(col, pen_w))
            p.setBrush(col if fill else Qt.NoBrush)

        if t == "Rect":
            w = max(1.0, a); h = max(1.0, b)
            r = QRectF(-w/2.0, -h/2.0, w, h); p.drawRect(r)
        elif t == "Circle":
            r = max(1.0, a); p.drawEllipse(QRectF(-r, -r, 2*r, 2*r))
        elif t == "Triangle":
            r = max(1.0, a); poly = QPolygon()
            for i in range(3):
                ang = -math.pi/2 + 2*math.pi*i/3
                poly.append(QPointF(math.cos(ang)*r, math.sin(ang)*r).toPoint())
            p.drawPolygon(poly)
        elif t == "NGon":
            r = max(1.0, a); n = max(3, min(24, sides)); poly = QPolygon()
            for i in range(n):
                ang = -math.pi/2 + 2*math.pi*i/n
                poly.append(QPointF(math.cos(ang)*r, math.sin(ang)*r).toPoint())
            p.drawPolygon(poly)
        elif t == "Line":
            L = max(1.0, a)
            c = _snap_center_for_pen(QPointF(0.0, 0.0), pen_w)
            p.drawLine(QLineF(QPointF(c.x() - L/2.0, c.y()), QPointF(c.x() + L/2.0, c.y())))
        elif t == "Cross":
            L = max(2.0, a); G = max(0.0, b)
            c = _snap_center_for_pen(QPointF(0.0, 0.0), pen_w)
            p.drawLine(QLineF(QPointF(c.x() - G/2.0 - L, c.y()), QPointF(c.x() - G/2.0, c.y())))
            p.drawLine(QLineF(QPointF(c.x() + G/2.0, c.y()),   QPointF(c.x() + G/2.0 + L, c.y())))
            p.drawLine(QLineF(QPointF(c.x(), c.y() - G/2.0 - L), QPointF(c.x(), c.y() - G/2.0)))
            p.drawLine(QLineF(QPointF(c.x(), c.y() + G/2.0),     QPointF(c.x(), c.y() + G/2.0 + L)))
        elif t == "XCross":
            L = max(2.0, a)
            p.drawLine(QLineF(QPointF(-L, -L), QPointF(L, L)))
            p.drawLine(QLineF(QPointF(-L,  L), QPointF(L, -L)))
        p.restore()

# ------------------ Кастомная палитра (диалог) ------------------
class ColorPaletteDialog(QDialog):
    PRESET = [
        "#FF0000","#FF6B6B","#FFA07A","#FF8C00","#FFA500","#FFD700",
        "#FFFF00","#ADFF2F","#00FF00","#32CD32","#00FA9A","#00FFFF",
        "#1E90FF","#0066FF","#0000FF","#7B68EE","#8A2BE2","#FF00FF",
        "#FF1493","#FF69B4","#FFFFFF","#C0C0C0","#808080","#404040",
        "#000000"
    ]

    def __init__(self, parent=None, initial_color: str="#FF0000", recent: Optional[List[str]]=None):
        super().__init__(parent, Qt.FramelessWindowHint)
        self.setModal(True)
        self.setMinimumWidth(360)
        self.selected_hex: Optional[str] = None

        # Заголовок
        self.tb = TitleBar(self, "Палитра цветов")
        root = QVBoxLayout(self); root.setContentsMargins(10,10,10,10); root.setSpacing(8)
        root.addWidget(self.tb)

        # Недавние
        self.recent_box = QGroupBox("Недавние")
        self.recent_row = QHBoxLayout(self.recent_box)
        self.recent_row.setContentsMargins(8,8,8,8)
        self.recent_row.setSpacing(6)
        if recent:
            self._set_recents(recent)
        else:
            self.recent_box.setVisible(False)
        root.addWidget(self.recent_box)

        # Пресеты
        box = QGroupBox("Палитра")
        grid = QGridLayout(box)
        grid.setContentsMargins(8,8,8,8)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)
        cols = 10
        for i, hx in enumerate(self.PRESET):
            r, c = divmod(i, cols)
            grid.addWidget(self._swatch(hx), r, c)
        root.addWidget(box)

        # Поле HEX + кнопки
        bottom = QHBoxLayout()
        self.hex_edit = QLineEdit(initial_color or "#FF0000")
        self.hex_edit.setPlaceholderText("#RRGGBB")
        bottom.addWidget(self.hex_edit, 1)
        self.btn_other = QPushButton("Другой…")
        self.btn_cancel = QPushButton("Отмена")
        self.btn_ok = QPushButton("OK")
        bottom.addWidget(self.btn_other)
        bottom.addStretch(1)
        bottom.addWidget(self.btn_cancel)
        bottom.addWidget(self.btn_ok)
        root.addLayout(bottom)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self._ok)
        self.btn_other.clicked.connect(self._other)

    def _swatch(self, hx: str) -> QToolButton:
        b = QToolButton()
        b.setFixedSize(24, 24)
        b.setCursor(Qt.PointingHandCursor)
        b.setToolTip(hx.upper())
        b.setStyleSheet(
            f"QToolButton {{ border:1px solid #2b2f3a; border-radius:5px; background:{hx}; }} "
            f"QToolButton:hover {{ border-color:#5AA9FF; }}"
        )
        b.clicked.connect(lambda: self._pick(hx))
        return b

    def _set_recents(self, colors: List[str]):
        # очистка
        while self.recent_row.count():
            item = self.recent_row.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()
        clean = []
        for hx in (colors or []):
            t = (hx or "").strip().upper()
            if len(t) in (4,7) and t.startswith("#"):
                if len(t) == 4:
                    t = "#" + "".join(ch*2 for ch in t[1:])
                if t not in clean:
                    clean.append(t)
        for hx in clean[:12]:
            self.recent_row.addWidget(self._swatch(hx))
        self.recent_box.setVisible(len(clean) > 0)

    def _pick(self, hx: str):
        self.selected_hex = self._sanitize_hex(hx)
        self.accept()

    def _ok(self):
        self.selected_hex = self._sanitize_hex(self.hex_edit.text())
        self.accept()

    def _other(self):
        col = QColorDialog.getColor(QColor(self._sanitize_hex(self.hex_edit.text())), self, "Выбор цвета")
        if col.isValid():
            self.selected_hex = col.name().upper()
            self.accept()

    @staticmethod
    def _sanitize_hex(txt: str) -> str:
        t = (txt or "").strip()
        t = ('#'+t) if t and not t.startswith('#') else t
        if len(t) == 4:
            t = '#' + ''.join(c*2 for c in t[1:])
        return (t[:7] or "#FF0000").upper()

# ------------------ Overlay ------------------
class OverlayWindow(QWidget):
    def __init__(self, screen_geometry, settings: Settings):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        try:
            self.setWindowFlag(Qt.WindowTransparentForInput, True)
        except Exception:
            pass
        self._settings = settings
        self._place(screen_geometry)

    def _place(self, screen_geometry):
        size = QSize(self._settings.canvas_size, self._settings.canvas_size)
        sc = screen_geometry
        cx, cy = sc.x() + sc.width()/2.0, sc.y() + sc.height()/2.0
        x = int(round(cx - size.width()/2.0))
        y = int(round(cy - size.height()/2.0))
        self.setGeometry(QRect(x, y, size.width(), size.height()))

    def apply(self, s: Settings, screen_geometry=None):
        self._settings = s
        if screen_geometry is not None:
            self._place(screen_geometry)
        self.update()

    def paintEvent(self, _):
        s = self._settings
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect()
        c = QPointF(rect.center()) + QPointF(float(s.offset_x), float(s.offset_y))
        scale = max(0.1, min(4.0, s.scale))
        objs = s.current_objects()
        hide_base = s.scene_hide_crosshair() or len(objs) > 0

        if not hide_base:
            penw = max(1, int(round(s.thickness * scale)))
            col = QColor(s.color_hex); col.setAlphaF(max(0.0, min(1.0, s.opacity)))
            p.setPen(QPen(col, penw))
            cc = _snap_center_for_pen(c, penw)

            if s.style == "Dot":
                dot_r = max(1, int(round((s.thickness + 1) * scale)))
                p.setBrush(col)
                p.drawEllipse(QRectF(cc.x()-dot_r, cc.y()-dot_r, 2*dot_r, 2*dot_r))
            else:
                if s.style in ("Cross", "CrossCircle"):
                    g = max(0.0, float(s.gap * scale)); L = max(2.0, float(s.length * scale))
                    p.drawLine(QLineF(QPointF(cc.x() - g - L, cc.y()), QPointF(cc.x() - g, cc.y())))
                    p.drawLine(QLineF(QPointF(cc.x() + g, cc.y()), QPointF(cc.x() + g + L, cc.y())))
                    p.drawLine(QLineF(QPointF(cc.x(), cc.y() - g - L), QPointF(cc.x(), cc.y() - g)))
                    p.drawLine(QLineF(QPointF(cc.x(), cc.y() + g), QPointF(cc.x(), cc.y() + g + L)))
                if s.style in ("Circle", "CrossCircle"):
                    R = max(2.0, float(s.radius * scale)); p.setBrush(Qt.NoBrush)
                    p.drawEllipse(QRectF(cc.x()-R, cc.y()-R, 2*R, 2*R))

        for obj in objs:
            ObjectPainter.draw_object(p, obj, c, view_scale=1.0, erase_preview=None)

# ------------------ Overlay manager ------------------
class OverlayManager:
    def __init__(self, app: QApplication, settings: Settings):
        self.app = app; self.settings = settings; self.overlays: List[OverlayWindow] = []
        self._create_per_screen()
    def _create_per_screen(self):
        self.overlays.clear()
        for screen in self.app.screens():
            self.overlays.append(OverlayWindow(screen.geometry(), self.settings))
        self.apply(self.settings)
    def recreate_geometry(self):
        for screen, wnd in zip(self.app.screens(), self.overlays):
            wnd.apply(self.settings, screen.geometry())
    def show(self):
        for w in self.overlays: w.show()
    def hide(self):
        for w in self.overlays: w.hide()
    def toggle(self): self.hide() if any(w.isVisible() for w in self.overlays) else self.show()
    def apply(self, s: Settings):
        for screen, w in zip(self.app.screens(), self.overlays): w.apply(s, screen.geometry())
        (self.show() if s.visible else self.hide())

# ------------------ Глобальный хоткей (Win) ------------------
if sys.platform.startswith('win'):
    user32 = ctypes.windll.user32
    WM_HOTKEY = 0x0312
    MOD_NOREPEAT = 0x4000
    VK_F8 = 0x77

    class WinHotkeyFilter(QAbstractNativeEventFilter):
        def __init__(self, cb):
            super().__init__(); self.cb = cb
        def nativeEventFilter(self, eventType, message):
            if eventType == b'windows_generic_MSG' or eventType == 'windows_generic_MSG':
                class MSG(ctypes.Structure):
                    _fields_ = [("hwnd", ctypes.c_void_p), ("message", ctypes.c_uint),
                                ("wParam", ctypes.c_void_p), ("lParam", ctypes.c_void_p),
                                ("time", ctypes.c_uint), ("pt_x", ctypes.c_int), ("pt_y", ctypes.c_int)]
                msg = MSG.from_address(int(message))
                if msg.message == WM_HOTKEY and int(msg.wParam) == 1:
                    QTimer.singleShot(0, self.cb)
            return False, 0

    def register_win_hotkey(app: QApplication, callback) -> bool:
        try:
            if not user32.RegisterHotKey(None, 1, MOD_NOREPEAT, VK_F8): return False
            filt = WinHotkeyFilter(callback)
            app._chl_hotkey_filter = filt
            app.installNativeEventFilter(filt)
            app.aboutToQuit.connect(lambda: user32.UnregisterHotKey(None, 1))
            return True
        except Exception:
            return False
else:
    def register_win_hotkey(app, callback) -> bool:
        return False

# ------------------ Кастомный TitleBar ------------------
class TitleBar(QWidget):
    def __init__(self, owner, title=""):
        super().__init__(owner)
        self.setObjectName("TitleBar")
        self.owner = owner
        lay = QHBoxLayout(self); lay.setContentsMargins(10,6,10,6); lay.setSpacing(10)
        self.lbl = QLabel(title); lay.addWidget(self.lbl); lay.addStretch(1)
        self.btn_min = QToolButton(); self.btn_min.setObjectName('winbtn'); self.btn_min.setText('—'); self.btn_min.setToolTip('Minimize')
        self.btn_max = QToolButton(); self.btn_max.setObjectName('winbtn'); self.btn_max.setText('▢'); self.btn_max.setToolTip('Maximize/Restore')
        self.btn_close = QToolButton(); self.btn_close.setObjectName('winbtn'); self.btn_close.setProperty('role','close'); self.btn_close.setText('×'); self.btn_close.setToolTip('Close')
        for b in (self.btn_min, self.btn_max, self.btn_close): lay.addWidget(b)
        self.btn_min.clicked.connect(owner.showMinimized)
        self.btn_max.clicked.connect(lambda: owner.showNormal() if owner.isMaximized() else owner.showMaximized())
        self.btn_close.clicked.connect(owner.close)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            try:
                self.window().windowHandle().startSystemMove()
            except Exception:
                self._drag = e.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if hasattr(self, "_drag") and (e.buttons() & Qt.LeftButton):
            self.window().move(e.globalPosition().toPoint() - self._drag)
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if hasattr(self, "_drag"): self._drag = None
        super().mouseReleaseEvent(e)

# ------------------ Текстовый диалог с нашим TitleBar ------------------
class TextInputDialog(QDialog):
    def __init__(self, title: str, label: str, parent=None, default_text=""):
        super().__init__(parent, Qt.FramelessWindowHint)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.tb = TitleBar(self, title)
        root = QVBoxLayout(self); root.setContentsMargins(10,10,10,10); root.setSpacing(8)
        root.addWidget(self.tb)
        box = QGroupBox(); box_l = QVBoxLayout(box); box_l.setContentsMargins(8,8,8,8)
        self.lbl = QLabel(label); self.edit = QLineEdit(default_text)
        box_l.addWidget(self.lbl); box_l.addWidget(self.edit)
        btns = QHBoxLayout(); ok = QPushButton("OK"); cancel = QPushButton("Cancel")
        btns.addStretch(1); btns.addWidget(ok); btns.addWidget(cancel)
        root.addWidget(box); root.addLayout(btns)
        ok.clicked.connect(self.accept); cancel.clicked.connect(self.reject)

    @staticmethod
    def get_text(title, label, parent=None, default_text=""):
        dlg = TextInputDialog(title, label, parent, default_text)
        ok = dlg.exec() == QDialog.Accepted
        return dlg.edit.text(), ok

# ------------------ Превью-виджет ------------------
class ScenePreview(QWidget):
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setMinimumHeight(240)
        self.setAutoFillBackground(False)

    def paintEvent(self, _):
        s = self.settings
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect()
        c = QPointF(rect.center())
        penw = max(1, int(round(s.thickness * s.scale)))
        col = QColor(s.color_hex); col.setAlphaF(max(0.0, min(1.0, s.opacity)))

        if not s.scene_hide_crosshair() and not s.current_objects():
            p.setPen(QPen(col, penw))
            cc = _snap_center_for_pen(c, penw)
            if s.style in ("Cross", "CrossCircle"):
                g = max(0.0, float(s.gap * s.scale)); L = max(2.0, float(s.length * s.scale))
                p.drawLine(QLineF(QPointF(cc.x() - g - L, cc.y()), QPointF(cc.x() - g, cc.y())))
                p.drawLine(QLineF(QPointF(cc.x() + g, cc.y()), QPointF(cc.x() + g + L, cc.y())))
                p.drawLine(QLineF(QPointF(cc.x(), cc.y() - g - L), QPointF(cc.x(), cc.y() - g)))
                p.drawLine(QLineF(QPointF(cc.x(), cc.y() + g), QPointF(cc.x(), cc.y() + g + L)))
            if s.style in ("Circle", "CrossCircle"):
                R = max(2.0, float(s.radius * s.scale)); p.setBrush(Qt.NoBrush)
                p.drawEllipse(QRectF(cc.x()-R, cc.y()-R, 2*R, 2*R))

        for obj in s.current_objects():
            ObjectPainter.draw_object(p, obj, c, view_scale=1.0, erase_preview=None)

# ------------------ MainWindow ------------------
class MainWindow(QMainWindow):
    RESIZE_MARGIN = 8

    def __init__(self, manager: OverlayManager, settings: Settings):
        super().__init__(); self.manager = manager; self.settings = settings
        self.setWindowTitle("CrosshairLite — settings"); self.setMinimumSize(QSize(980, 640)); self.resize(QSize(1200, 760))
        self.setWindowFlag(Qt.FramelessWindowHint, True)

        self._build_ui()
        self._init_tray()
        self._load_to_ui(settings)

        # size grip + курсор по краям
        self._grip = QSizeGrip(self); self._grip.setFixedSize(18,18)

    def t(self, key: str) -> str: return self.settings.t(key)

    # ------- Supabase helpers -------
    def _sb_headers(self, extra: dict | None = None) -> dict:
        h = {'apikey': SUPABASE_ANON, 'Authorization': f'Bearer {SUPABASE_ANON}', 'User-Agent': 'CrosshairLite'}
        if extra: h.update(extra)
        return h
    def _sb_get_json(self, url: str, timeout: int = 12):
        try:
            req = urllib.request.Request(url, headers=self._sb_headers({'Accept':'application/json'}))
            with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:
            return None
    def _http_get_json(self, url: str) -> Optional[dict|list]:
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'CrosshairLite'})
            with urllib.request.urlopen(req, timeout=12, context=SSL_CTX) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:
            return None
    def _sb_put_bytes(self, path: str, data: bytes, content_type: str) -> bool:
        url = f"{STORAGE}/{SUPABASE_STORAGE_BUCKET}/{path.lstrip('/')}"
        try:
            req = urllib.request.Request(url, data=data, method="PUT", headers=self._sb_headers({'Content-Type': content_type, 'x-upsert': 'true'}))
            with urllib.request.urlopen(req, timeout=30, context=SSL_CTX) as _:
                return True
        except Exception:
            return False
    def _sb_insert_preset(self, rec: dict) -> bool:
        url = f"{REST}/presets"
        try:
            data = json.dumps(rec).encode('utf-8')
            req = urllib.request.Request(url, data=data, method="POST", headers=self._sb_headers({'Content-Type':'application/json'}))
            with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as _:
                return True
        except Exception:
            return False

    # ---------------- UI ----------------
    def _build_ui(self):
        root = QWidget(); self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        # кастомный бар
        self.topbar = TitleBar(self, "CrosshairLite — settings")
        layout.addWidget(self.topbar)

        # Tabs
        tabs = QTabWidget(self); layout.addWidget(tabs, 1)

        # Cross tab (compact)
        w_cross = QWidget(); w_cross.setObjectName("CrossTab")
        tabs.addTab(w_cross, self.t('tab_crosshair'))

        v = QVBoxLayout(w_cross); v.setContentsMargins(12,12,12,12); v.setSpacing(10)
        top = QHBoxLayout(); v.addLayout(top)
        self.lbl_hint = QLabel(self.t('hint_toggle')); top.addWidget(self.lbl_hint); top.addStretch(1)
        self.lbl_lang = QLabel(self.t('lang')); self.cmb_lang = QComboBox(); self.cmb_lang.addItems(['English','Русский'])
        self.cmb_lang.setCurrentIndex(1 if self.settings.lang=='ru' else 0)
        top.addWidget(self.lbl_lang); top.addWidget(self.cmb_lang)

        box_style = QGroupBox(self.t('base_settings')); v.addWidget(box_style)
        form = QFormLayout(box_style)
        self.cmb_style = QComboBox(); self.cmb_style.addItems(["Dot","Cross","Circle","CrossCircle"])
        form.addRow(self.t('style'), self.cmb_style)

        # --- Цвет: HEX + кнопка палитры (диалог) ---
        box_color = QGroupBox(self.t('color')); v.addWidget(box_color)
        h = QHBoxLayout(box_color); h.setContentsMargins(8,8,8,8); h.setSpacing(8)
        self.hex_edit = QLineEdit("#FF0000"); h.addWidget(self.hex_edit, 1)
        self.btn_palette = QToolButton(); self.btn_palette.setText("🎨"); self.btn_palette.setToolTip("Открыть палитру")
        self.btn_palette.setFixedWidth(40)
        h.addWidget(self.btn_palette, 0)

        box_sizes = QGroupBox(self.t('sizes')); v.addWidget(box_sizes)
        g = QFormLayout(box_sizes)
        self.spin_thick = self._spin(1, 50, 2); self.spin_len = self._spin(2, 400, 24)
        self.spin_gap = self._spin(0, 200, 6); self.spin_rad = self._spin(2, 400, 18)
        self.spin_scale = self._spin_double(0.25, 4.0, 1.0, 0.05)
        g.addRow(self.t('thickness'), self._pair(self._slider(1,50,2), self.spin_thick))
        g.addRow(self.t('ray_length'), self._pair(self._slider(2,400,24), self.spin_len))
        g.addRow(self.t('gap'), self._pair(self._slider(0,200,6), self.spin_gap))
        g.addRow(self.t('radius'), self._pair(self._slider(2,400,18), self.spin_rad))
        g.addRow(self.t('scale_pct'), self._pair(self._slider(25,400,100), self.spin_scale, is_percent=True))

        box_offsets = QGroupBox(self.t('position')); v.addWidget(box_offsets)
        gh = QHBoxLayout(box_offsets)
        self.offx = self._spin(-2000,2000,0); self.offy = self._spin(-2000,2000,0)
        gh.addWidget(QLabel(self.t('x'))); gh.addWidget(self.offx); gh.addSpacing(16)
        gh.addWidget(QLabel(self.t('y'))); gh.addWidget(self.offy); gh.addStretch(1)

        row = QHBoxLayout(); v.addLayout(row)
        self.btn_toggle = QPushButton(self.t('toggle')); self.btn_save = QPushButton(self.t('save'))
        row.addStretch(1); row.addWidget(self.btn_toggle); row.addWidget(self.btn_save)

        # Scenes tab
        w_scn = QWidget(); w_scn.setObjectName("ScenesTab")
        tabs.addTab(w_scn, self.t('tab_scenes'))
        vs = QVBoxLayout(w_scn); vs.setContentsMargins(12,12,12,12)

        box_sc = QGroupBox(self.t('scenes_presets')); vs.addWidget(box_sc)
        grid = QGridLayout(box_sc)
        self.cmb_scene = QComboBox()
        self.chk_scene_hide = QCheckBox(self.t('hide_crosshair'))
        self.btn_scene_new = QPushButton(self.t('create_scene'))
        self.btn_scene_del = QPushButton(self.t('delete'))
        self.btn_scene_fs  = QPushButton(self.t('fs_editor'))
        self.btn_scene_publish = QPushButton(self.t('publish'))
        grid.addWidget(QLabel(self.t('current')), 0,0)
        grid.addWidget(self.cmb_scene, 0,1,1,2)
        grid.addWidget(self.chk_scene_hide, 0,3,1,2)
        grid.addWidget(self.btn_scene_new, 0,5)
        grid.addWidget(self.btn_scene_del, 0,6)
        grid.addWidget(self.btn_scene_fs,  0,7)
        grid.addWidget(self.btn_scene_publish, 0,8)

        # community catalog
        box_comm = QGroupBox(self.settings.t('community')); vs.addWidget(box_comm, 1)
        lc = QVBoxLayout(box_comm); lc.setContentsMargins(8,8,8,8); lc.setSpacing(8)
        rowc = QHBoxLayout(); lc.addLayout(rowc)
        self.comm_search  = QLineEdit(); self.comm_search.setPlaceholderText(self.t('community_search'))
        self.comm_refresh = QPushButton(self.t('refresh'))
        rowc.addWidget(self.comm_search, 1); rowc.addWidget(self.comm_refresh)
        self.comm_list = QListWidget(); self.comm_list.setViewMode(QListWidget.IconMode)
        self.comm_list.setResizeMode(QListWidget.Adjust); self.comm_list.setMovement(QListWidget.Static)
        self.comm_list.setIconSize(QSize(128,128)); self.comm_list.setGridSize(QSize(170, 200)); self.comm_list.setSpacing(8)
        self.comm_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lc.addWidget(self.comm_list, 1)

        # Editor tab
        w_edit = QWidget(); w_edit.setObjectName("EditorTab")
        tabs.addTab(w_edit, self.t('editor'))
        ve = QHBoxLayout(w_edit); ve.setContentsMargins(12,12,12,12)

        # layers
        left = QVBoxLayout(); ve.addLayout(left, 1)
        self.list_objs = QListWidget(); left.addWidget(self.list_objs, 1)
        rowe = QHBoxLayout(); left.addLayout(rowe)
        self.btn_add = QPushButton(self.t('add_object')); self.btn_dup = QPushButton(self.t('duplicate')); self.btn_del = QPushButton(self.t('delete'))
        rowe.addWidget(self.btn_add); rowe.addWidget(self.btn_dup); rowe.addWidget(self.btn_del)

        # properties + preview
        right = QVBoxLayout(); ve.addLayout(right, 2)
        box_props = QGroupBox("Свойства"); right.addWidget(box_props, 2)
        props_outer = QVBoxLayout(box_props); props_outer.setContentsMargins(8,8,8,8); props_outer.setSpacing(8)
        self.props_widget = QWidget()
        self.props = QFormLayout(self.props_widget); self.props.setLabelAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.props.setFormAlignment(Qt.AlignTop)
        self.props.setHorizontalSpacing(12); self.props.setSpacing(8)

        self.ed_x = self._spin(-3000,3000,0); self.ed_y = self._spin(-3000,3000,0)
        self.ed_rot = self._dspin(-360,360,0.0,0.1); self.ed_scale = self._dspin(0.1,4.0,1.0,0.05)
        self.ed_a = self._spin(1,2000,40); self.ed_b = self._spin(0,2000,30)
        self.ed_th = self._spin(1,50,2)
        self.ed_fill = QCheckBox(self.t('fill')); self.ed_cut = QCheckBox(self.t('cut'))

        # --- цвет в редакторе: HEX + кнопка палитры
        self.ed_hex = QLineEdit("#FF0000")
        self.ed_color_palette = QToolButton()
        self.ed_color_palette.setText("🎨")
        self.ed_color_palette.setToolTip("Открыть палитру")
        self.ed_color_palette.setFixedWidth(40)

        w_color = QWidget()
        hl_color = QHBoxLayout(w_color)
        hl_color.setContentsMargins(0,0,0,0)
        hl_color.setSpacing(8)
        hl_color.addWidget(self.ed_hex, 1)
        hl_color.addWidget(self.ed_color_palette, 0)

        self.ed_op = self._dspin(0.0,1.0,1.0,0.05)

        self.props.addRow("X", self.ed_x); self.props.addRow("Y", self.ed_y)
        self.props.addRow(self.t('rot'), self.ed_rot); self.props.addRow("Scale", self.ed_scale)
        self.props.addRow("Size A", self.ed_a); self.props.addRow("Size B/Gap", self.ed_b)
        self.props.addRow(self.t('thickness'), self.ed_th)
        self.props.addRow(self.t('fill'), self.ed_fill); self.props.addRow(self.t('cut'), self.ed_cut)
        self.props.addRow(self.t('color'), w_color)
        self.props.addRow(self.t('alpha'), self.ed_op)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(self.props_widget)
        props_outer.addWidget(scroll, 1)

        self.preview = ScenePreview(self.settings); right.addWidget(self.preview, 1)

        # --- signals
        widgets = [self.cmb_style, self.hex_edit, self.spin_thick, self.spin_len, self.spin_gap, self.spin_rad, self.spin_scale, self.offx, self.offy]
        for w in widgets:
            if isinstance(w, QComboBox): w.currentIndexChanged.connect(self._auto_apply)
            elif isinstance(w, QLineEdit): w.editingFinished.connect(self._auto_apply)
            else: w.valueChanged.connect(self._auto_apply)

        self.btn_palette.clicked.connect(self._open_palette_dialog)

        self.btn_save.clicked.connect(self._save)
        self.btn_toggle.clicked.connect(self._toggle)
        self.cmb_lang.currentIndexChanged.connect(self._on_lang_change)

        # scenes
        self.btn_scene_new.clicked.connect(self._scene_new)
        self.btn_scene_del.clicked.connect(self._scene_delete)
        self.btn_scene_fs.clicked.connect(lambda: tabs.setCurrentWidget(w_edit))
        self.btn_scene_publish.clicked.connect(self._scene_publish_to_community)
        self.cmb_scene.currentTextChanged.connect(self._on_scene_combo)
        self.chk_scene_hide.toggled.connect(self._on_scene_hide_toggle)

        # editor
        self.btn_add.clicked.connect(self._add_object_menu)
        self.btn_dup.clicked.connect(self._dup_object)
        self.btn_del.clicked.connect(self._del_object)
        self.list_objs.currentRowChanged.connect(self._load_selected_object)
        for w in (self.ed_x,self.ed_y,self.ed_a,self.ed_b,self.ed_th):
            w.valueChanged.connect(self._apply_obj_props)
        for w in (self.ed_rot,self.ed_scale,self.ed_op):
            w.valueChanged.connect(self._apply_obj_props)
        for w in (self.ed_fill,self.ed_cut):
            w.toggled.connect(self._apply_obj_props)
        self.ed_hex.editingFinished.connect(self._apply_obj_props)
        self.ed_color_palette.clicked.connect(self._open_editor_palette_dialog)

        # community
        self.comm_refresh.clicked.connect(self._community_search)
        self.comm_search.textChanged.connect(lambda _: self._community_search())
        self.comm_list.itemDoubleClicked.connect(self._community_import_item)

        # show cached community then fetch
        self._community_render_supabase(self._community_load_cache())
        QTimer.singleShot(0, self._community_search)

    # --- utils UI
    def _slider(self,a,b,v): s = QSlider(Qt.Horizontal); s.setRange(a,b); s.setValue(v); return s
    def _spin(self,a,b,v): sp = QSpinBox(); sp.setRange(a,b); sp.setValue(v); return sp
    def _dspin(self,a,b,v,step): sp = QDoubleSpinBox(); sp.setDecimals(2); sp.setRange(a,b); sp.setSingleStep(step); sp.setValue(v); return sp
    def _spin_double(self,a,b,v,step=0.1): return self._dspin(a,b,v,step)
    def _pair(self, slider:QSlider, spin, is_percent=False):
        w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(0,0,0,0); h.addWidget(slider,1); h.addSpacing(8); h.addWidget(spin)
        if is_percent:
            def on_s(val): spin.setValue(val/100.0)
            def on_p(val): slider.setValue(int(round(val*100)))
            slider.valueChanged.connect(on_s); spin.valueChanged.connect(on_p)
        else:
            slider.valueChanged.connect(spin.setValue); spin.valueChanged.connect(slider.setValue)
        return w

    # --- tray
    def _make_tray_icon(self) -> QIcon:
        px = QPixmap(16,16); px.fill(Qt.transparent); p = QPainter(px); p.setRenderHint(QPainter.Antialiasing, True)
        p.setBrush(QColor("#00FF00")); p.setPen(Qt.NoPen); p.drawEllipse(px.rect().center(), 6, 6); p.end(); return QIcon(px)
    def _init_tray(self):
        self.tray = QSystemTrayIcon(self); icon = self._make_tray_icon()
        if icon.isNull(): icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray.setIcon(icon); m = QMenu()
        act_show = QAction("Settings", self); act_show.triggered.connect(self.showNormal); m.addAction(act_show)
        act_toggle = QAction("Show/Hide (F8)", self); act_toggle.triggered.connect(self._toggle); m.addAction(act_toggle)
        act_exit = QAction("Exit", self); act_exit.triggered.connect(QApplication.instance().quit); m.addAction(act_exit)
        self.tray.setContextMenu(m); self.tray.setVisible(True)

    # --- перетаскивание/ресайз без рамки
    def resizeEvent(self, e):
        try:
            if hasattr(self, '_grip') and self._grip is not None:
                self._grip.move(self.width()-self._grip.width()-6, self.height()-self._grip.height()-6)
        except Exception: pass
        super().resizeEvent(e)

    def _edges_at(self, pos):
        m = self.RESIZE_MARGIN
        r = self.rect()
        edges = Qt.Edges()
        if pos.x() <= m: edges |= Qt.LeftEdge
        if pos.x() >= r.width()-m: edges |= Qt.RightEdge
        if pos.y() <= m: edges |= Qt.TopEdge
        if pos.y() >= r.height()-m: edges |= Qt.BottomEdge
        return edges

    def mousePressEvent(self, e):
        if e.button()==Qt.LeftButton:
            edges = self._edges_at(e.pos())
            if edges:
                try:
                    self.windowHandle().startSystemResize(edges)
                    e.accept(); return
                except Exception:
                    pass
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        edges = self._edges_at(e.pos())
        cur = Qt.ArrowCursor
        if edges:
            left  = bool(edges & Qt.LeftEdge)
            right = bool(edges & Qt.RightEdge)
            top   = bool(edges & Qt.TopEdge)
            bot   = bool(edges & Qt.BottomEdge)
            if (left and top) or (right and bot): cur = Qt.SizeFDiagCursor
            elif (right and top) or (left and bot): cur = Qt.SizeBDiagCursor
            elif left or right: cur = Qt.SizeHorCursor
            elif top or bot: cur = Qt.SizeVerCursor
        self.setCursor(cur)
        super().mouseMoveEvent(e)

    # --- settings <-> ui
    def _load_to_ui(self, s: Settings):
        self.cmb_style.setCurrentText(s.style if s.style in ("Dot","Cross","Circle","CrossCircle") else "Cross")
        self.hex_edit.setText(s.color_hex)
        self.spin_thick.setValue(s.thickness); self.spin_len.setValue(s.length)
        self.spin_gap.setValue(s.gap); self.spin_rad.setValue(s.radius)
        self.spin_scale.setValue(s.scale); self.offx.setValue(s.offset_x); self.offy.setValue(s.offset_y)
        self._refresh_scene_combo()
        self.preview.update()

    def _read_from_ui(self) -> Settings:
        s = self.settings
        s.style = self.cmb_style.currentText(); s.color_hex = self._sanitize_hex(self.hex_edit.text())
        s.thickness = int(self.spin_thick.value()); s.length = int(self.spin_len.value())
        s.gap = int(self.spin_gap.value()); s.radius = int(self.spin_rad.value())
        s.scale = float(self.spin_scale.value()); s.offset_x = int(self.offx.value()); s.offset_y = int(self.offy.value())
        return s

    def _sanitize_hex(self, txt: str) -> str:
        t = (txt or "").strip(); t = ('#'+t) if t and not t.startswith('#') else t
        if len(t) == 4: t = '#' + ''.join(c*2 for c in t[1:])
        return (t[:7] or "#FF0000").upper()

    # --- scenes
    def _refresh_scene_combo(self):
        self.cmb_scene.blockSignals(True); self.cmb_scene.clear()
        names = sorted(self.settings.scenes.keys())
        if not names: self.settings.scenes["Default"] = self.settings.scene_from_self(); names = ["Default"]
        self.cmb_scene.addItems(names)
        idx = self.cmb_scene.findText(self.settings.active_scene); self.cmb_scene.setCurrentIndex(max(0, idx))
        self.cmb_scene.blockSignals(False)
        self.chk_scene_hide.setChecked(self.settings.scene_hide_crosshair())

    def _scene_new(self):
        base = "Scene"; i = 1
        while f"{base} {i}" in self.settings.scenes: i+=1
        name = f"{base} {i}"
        self.settings.scenes[name] = self.settings.scene_from_self()
        self.settings.scenes[name]["objects"] = []
        self.settings.scenes[name]["hide_crosshair"] = True
        self.settings.active_scene = name; self.settings.save()
        self._refresh_scene_combo()
        self._on_scene_combo(name)

    def _scene_delete(self):
        name = self.cmb_scene.currentText()
        if name and name in self.settings.scenes:
            del self.settings.scenes[name]
            if not self.settings.scenes:
                self.settings.scenes["Default"] = self.settings.scene_from_self(); self.settings.active_scene = "Default"
            else:
                self.settings.active_scene = next(iter(self.settings.scenes.keys()))
            self.settings.save(); self._refresh_scene_combo(); self._auto_apply()

    def _on_scene_combo(self, name: str):
        if not name: return
        self.settings.apply_scene_to_self(name)
        self._load_to_ui(self.settings)
        self.manager.apply(self.settings)
        self.settings.save()
        self._reload_objs_list()
        self.preview.update()

    def _on_scene_hide_toggle(self, val: bool):
        name = self.cmb_scene.currentText(); sc = self.settings.scenes.setdefault(name, {})
        sc["hide_crosshair"] = bool(val); self._auto_apply()

    # --- editor objects
    def _reload_objs_list(self):
        self.list_objs.clear()
        for o in self.settings.current_objects():
            t = o.get('type','?')
            self.list_objs.addItem(t)
        if self.list_objs.count() > 0:
            self.list_objs.setCurrentRow(self.list_objs.count()-1)

    def _add_object_menu(self):
        m = QMenu(self)
        types = ["Circle","Rect","Line","Cross","XCross","Triangle","NGon"]
        acts = {m.addAction(t): t for t in types}
        act = m.exec(self.btn_add.mapToGlobal(self.btn_add.rect().bottomLeft()))
        if not act: return
        typ = acts[act]
        a,b = {"Circle":(40,0),"Rect":(60,40),"Line":(120,0),"Cross":(40,8),"XCross":(40,0),"Triangle":(40,0),"NGon":(40,0)}.get(typ,(40,0))
        obj = {"type":typ,"x":0,"y":0,"rotation":0.0,"scale":1.0,"size_a":a,"size_b":b,"thickness":2,"fill":False,
               "color_hex":"#FF0000","opacity":1.0,"sides":5,"cut":False}
        objs = self.settings.current_objects(); objs.append(obj); self.settings.set_current_objects(objs); self.settings.save()
        self._reload_objs_list(); self.preview.update()

    def _dup_object(self):
        i = self.list_objs.currentRow()
        if i < 0: return
        objs = self.settings.current_objects()
        dup = dict(objs[i]); dup['x'] = int(dup.get('x',0)+20); dup['y'] = int(dup.get('y',0)+20)
        objs.insert(i+1, dup); self.settings.set_current_objects(objs); self.settings.save()
        self._reload_objs_list(); self.list_objs.setCurrentRow(i+1); self.preview.update()

    def _del_object(self):
        i = self.list_objs.currentRow()
        if i < 0: return
        objs = self.settings.current_objects()
        objs.pop(i); self.settings.set_current_objects(objs); self.settings.save()
        self._reload_objs_list(); self.preview.update()

    def _load_selected_object(self, idx: int):
        objs = self.settings.current_objects()
        if 0 <= idx < len(objs):
            o = objs[idx]
            self.ed_x.setValue(int(o.get('x',0))); self.ed_y.setValue(int(o.get('y',0)))
            self.ed_rot.setValue(float(o.get('rotation',0.0))); self.ed_scale.setValue(float(o.get('scale',1.0)))
            self.ed_a.setValue(int(o.get('size_a',40))); self.ed_b.setValue(int(o.get('size_b',30)))
            self.ed_th.setValue(int(o.get('thickness',2))); self.ed_fill.setChecked(bool(o.get('fill',False)))
            self.ed_cut.setChecked(bool(o.get('cut',False))); self.ed_hex.setText(o.get('color_hex','#FF0000'))
            self.ed_op.setValue(float(o.get('opacity',1.0)))

    def _apply_obj_props(self, *_):
        idx = self.list_objs.currentRow()
        objs = self.settings.current_objects()
        if 0 <= idx < len(objs):
            o = objs[idx]
            o.update({
                'x': int(self.ed_x.value()), 'y': int(self.ed_y.value()),
                'rotation': float(self.ed_rot.value()), 'scale': float(self.ed_scale.value()),
                'size_a': int(self.ed_a.value()), 'size_b': int(self.ed_b.value()),
                'thickness': int(self.ed_th.value()), 'fill': bool(self.ed_fill.isChecked()),
                'cut': bool(self.ed_cut.isChecked()),
                'color_hex': self._sanitize_hex(self.ed_hex.text()),
                'opacity': float(self.ed_op.value())
            })
            self.settings.set_current_objects(objs); self.settings.save()
            self.preview.update(); self.manager.apply(self.settings)

    # ---- Палитры (кнопки-диалоги) ----
    def _open_palette_dialog(self):
        init = self._sanitize_hex(self.hex_edit.text())
        dlg = ColorPaletteDialog(self, initial_color=init, recent=self.settings.recent_colors)
        if dlg.exec() == QDialog.Accepted and dlg.selected_hex:
            self.hex_edit.setText(dlg.selected_hex)
            self._apply_from_ui()
            self._add_recent_color(dlg.selected_hex)

    def _open_editor_palette_dialog(self):
        init = self._sanitize_hex(self.ed_hex.text())
        dlg = ColorPaletteDialog(self, initial_color=init, recent=self.settings.recent_colors)
        if dlg.exec() == QDialog.Accepted and dlg.selected_hex:
            self.ed_hex.setText(dlg.selected_hex)
            self._apply_obj_props()           # применяем к текущему объекту
            self._add_recent_color(dlg.selected_hex)

    def _add_recent_color(self, hx: str):
        hx = self._sanitize_hex(hx)
        cur = [c.upper() for c in (self.settings.recent_colors or [])]
        new = [hx] + [c for c in cur if c != hx]
        self.settings.recent_colors = new[:12]
        self.settings.save()

    # ---- Перезапуск приложения ----
    def _restart_app(self):
        try:
            self.settings.save()
        except Exception:
            pass
        program = sys.executable
        args = list(sys.argv)
        QProcess.startDetached(program, args)
        QApplication.instance().quit()

    # ---- Community (Supabase) ----
    def _community_cache_file(self) -> str:
        return os.path.join(cache_dir(), "comm_index.json")
    def _community_load_cache(self) -> list:
        try:
            with open(self._community_cache_file(), "r", encoding="utf-8") as f:
                rows = json.load(f)
            return rows if isinstance(rows, list) else []
        except Exception:
            return []
    def _community_save_cache(self, rows: list):
        try:
            with open(self._community_cache_file(), "w", encoding="utf-8") as f:
                json.dump(rows, f, ensure_ascii=False)
        except Exception:
            pass
    def _community_get_thumb(self, url: str) -> QPixmap | None:
        fn = os.path.join(cache_dir(), hashlib.sha1(url.encode('utf-8')).hexdigest() + ".png")
        if os.path.exists(fn):
            px = QPixmap(fn)
            if not px.isNull(): return px
        try:
            req = urllib.request.Request(url, headers=self._sb_headers())
            with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as r: data = r.read()
            with open(fn, 'wb') as f: f.write(data)
            px = QPixmap(); px.loadFromData(data); return px if not px.isNull() else None
        except Exception:
            return None
    def _community_render_supabase(self, rows: list):
        self.comm_list.clear()
        for r in (rows or []):
            name   = str(r.get('name', '')).strip()
            author = str(r.get('author', '')).strip()
            icon = QIcon()
            tp = (r.get('thumb_path') or '').strip()
            if tp:
                turl = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_STORAGE_BUCKET}/{tp}"
                px = self._community_get_thumb(turl)
                if px and not px.isNull():
                    icon = QIcon(px)
            text = name if not author else f"{name} · {author}"
            item = QListWidgetItem(icon, text)
            item.setData(Qt.UserRole, r)
            item.setSizeHint(QSize(170, 190))
            self.comm_list.addItem(item)
    def _community_search(self):
        url = f"{REST}/presets?select=*&approved=eq.true&order=updated.desc"
        rows = self._sb_get_json(url)
        if not isinstance(rows, list):
            cached = self._community_load_cache()
            if self.comm_list.count() == 0 and cached:
                self._community_render_supabase(cached)
            return
        self._community_save_cache(rows)
        q = (self.comm_search.text() or "").strip().lower()
        if q:
            rows = [r for r in rows if q in (r.get('name','') or '').lower()
                                  or q in ' '.join(r.get('tags') or []).lower()
                                  or q in (r.get('author','') or '').lower()]
        self._community_render_supabase(rows)
    def _community_import_item(self, item: QListWidgetItem):
        r = item.data(Qt.UserRole) or {}
        rec_id = str(r.get('id') or '')
        # если уже импортирован — просто активируем
        for name, scene in self.settings.scenes.items():
            origin = scene.get('_origin') or {}
            if origin.get('provider')=='supabase' and str(origin.get('id'))==rec_id:
                self.settings.active_scene = name; self.settings.save()
                self._refresh_scene_combo(); self._on_scene_combo(name)
                return
        path = r.get('scene_path')
        if not path: return
        uid = os.path.splitext(os.path.basename(path))[0]
        cache_fn = os.path.join(cache_dir(), f"{uid}.chl.json")
        data = None
        if os.path.exists(cache_fn):
            try:
                with open(cache_fn, "r", encoding="utf-8") as f: data = json.load(f)
            except Exception: data = None
        if data is None:
            url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_STORAGE_BUCKET}/{path}"
            data = self._http_get_json(url)
            if isinstance(data, (dict,list)):
                try:
                    with open(cache_fn, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False)
                except Exception:
                    pass
        if not isinstance(data, dict):
            QMessageBox.warning(self, "Import", "Invalid preset payload"); return
        if 'scene' in data and isinstance(data['scene'], dict): name, scene = (data.get('name') or r.get('name') or "Imported"), data['scene']
        else: name, scene = (r.get('name') or "Imported"), data
        base = name; i = 2
        while name in self.settings.scenes: name = f"{base} ({i})"; i += 1
        scene['_origin'] = {'provider':'supabase','id':rec_id}
        self.settings.scenes[name] = scene; self.settings.active_scene = name
        self.settings.save(); self._refresh_scene_combo(); self._on_scene_combo(name)
    def _render_scene_preview(self, scene: dict) -> QPixmap:
        size = 256; pm = QPixmap(size, size); pm.fill(Qt.transparent)
        p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing, True)
        c = QPointF(size/2.0, size/2.0); s = Settings()
        for k in ("style","color_hex","opacity","thickness","length","gap","radius","scale","offset_x","offset_y"):
            if k in scene: setattr(s, k, scene[k])
        objs = scene.get("objects", [])
        if not scene.get("hide_crosshair", False) and not objs:
            penw = max(1, int(round(s.thickness * s.scale)))
            col = QColor(s.color_hex)
            p.setPen(QPen(col, penw))
            cc = _snap_center_for_pen(c, penw)
            g = max(0.0, float(s.gap * s.scale)); L = max(2.0, float(s.length * s.scale))
            p.drawLine(QLineF(QPointF(cc.x() - g - L, c.y()), QPointF(cc.x() - g, c.y())))
            p.drawLine(QLineF(QPointF(cc.x() + g, c.y()), QPointF(cc.x() + g + L, c.y())))
            p.drawLine(QLineF(QPointF(c.x(), c.y() - g - L), QPointF(c.x(), c.y() - g)))
            p.drawLine(QLineF(QPointF(c.x(), c.y() + g), QPointF(c.x(), c.y() + g + L)))
        for obj in objs: ObjectPainter.draw_object(p, obj, c, view_scale=1.0, erase_preview=None)
        p.end(); return pm
    def _scene_publish_to_community(self):
        name = self.cmb_scene.currentText().strip() or "Untitled"
        scene = self.settings.scenes.get(name, self.settings.scene_from_self())
        tags_str, ok = TextInputDialog.get_text(self.t('publish'), "Теги (через запятую):", self, "")
        if not ok: return
        tags = [t.strip() for t in tags_str.split(',') if t.strip()]
        try:
            author = os.getlogin()
        except Exception:
            author = "anon"
        uid = uuid.uuid4().hex
        scene_json = json.dumps({"name": name, "scene": scene}, ensure_ascii=False, indent=2).encode('utf-8')
        scene_path = f"scenes/{uid}.chl.json"; ok1 = self._sb_put_bytes(scene_path, scene_json, "application/json")
        thumb_path = None
        try:
            px = self._render_scene_preview(scene); ba = QByteArray(); buf = QBuffer(ba); buf.open(QBuffer.ReadWrite); px.save(buf, "PNG")
            thumb_path = f"thumbs/{uid}.png"; _ = self._sb_put_bytes(thumb_path, bytes(ba), "image/png")
        except Exception:
            pass
        if not ok1:
            QMessageBox.warning(self, "Community", "Upload failed."); return
        rec = {"name": name, "author": author, "tags": tags, "scene_path": scene_path, "thumb_path": thumb_path, "approved": True}
        ok3 = self._sb_insert_preset(rec)
        QMessageBox.information(self, "Community", "Отправлено." if ok3 else "Record insert failed.")

    # --- apply/save
    def _apply_from_ui(self):
        self.settings = self._read_from_ui(); self.manager.apply(self.settings); self.preview.update()
    def _auto_apply(self): self._apply_from_ui() if True else None
    def _save(self): self._apply_from_ui(); self.settings.save()
    def _toggle(self): self.manager.toggle()
    def _on_lang_change(self, idx: int):
        new_lang = 'en' if idx == 0 else 'ru'
        if self.settings.lang != new_lang:
            self.settings.lang = new_lang
            self.settings.save()
            # небольшая задержка для спокойной записи файла, затем перезапуск
            QTimer.singleShot(150, self._restart_app)

# ------------------ main ------------------
def start_global_hotkey(app: QApplication, toggle_cb):
    register_win_hotkey(app, toggle_cb)

def main():
    # Масштаб интерфейса строго 1.0
    os.environ["QT_SCALE_FACTOR"] = "1"
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_QSS)
    settings = Settings.load()
    manager = OverlayManager(app, settings)
    wnd = MainWindow(manager, settings); wnd.show()
    start_global_hotkey(app, manager.toggle)
    (manager.show() if settings.visible else manager.hide())
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
