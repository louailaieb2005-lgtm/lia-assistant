"""
LIA - PySide6 application setup and layout using Fluent Widgets.
"""

import threading
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QSize, QThread
from PySide6.QtGui import QIcon

from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon as FIF,
    SplashScreen
)

# ... (كل الاستيرادات الأخرى تبقى كما هي بدون تغيير) ...

class MainWindow(FluentWindow):
    """Main application window using Fluent Design - LIA Edition."""
    
    def __init__(self):
        super().__init__()
        # التعديل: تغيير اسم النافذة إلى LIA
        self.setWindowTitle("LIA - Algerian AI") 
        self.setMinimumSize(1100, 750)
        self.resize(1200, 800)
        
        self.setStyleSheet(AURA_STYLESHEET)
        
        # Initialize handlers
        self.handlers = ChatHandlers(self)
        
        # Add system monitor to title bar
        self._init_system_monitor()
        
        # Initialize sub-interfaces pointers
        self.chat_tab = None
        self.planner_tab = None
        self.briefing_view = None
        self.home_tab = None
        
        self._chat_signals_connected = False

        self._init_window()
        self._connect_signals()
        self._init_background()
        self._preload_models()
        self._init_voice_assistant()
        
    def _init_voice_assistant(self):
        """Initialize and start LIA voice assistant."""
        # التعديل: تحديث رسائل الكونسول لتظهر باسم LIA
        print(f"[App] Initializing LIA (enabled={VOICE_ASSISTANT_ENABLED})...")
        if VOICE_ASSISTANT_ENABLED:
            voice_assistant.wake_word_detected.connect(self._on_wake_word_detected)
            voice_assistant.speech_recognized.connect(self._on_speech_recognized)
            voice_assistant.processing_finished.connect(self._on_processing_finished)
            voice_assistant.timer_set.connect(self._on_voice_timer_set)
            voice_assistant.alarm_added.connect(self._on_voice_alarm_added)
            voice_assistant.calendar_updated.connect(self._on_voice_calendar_updated)
            voice_assistant.task_added.connect(self._on_voice_task_added)
            
            def init_va():
                if voice_assistant.initialize():
                    tts.toggle(True)
                    # جعل الصوت العربي أسرع قليلاً للاستجابة المرحة
                    if hasattr(tts, 'set_rate'): tts.set_rate("+15%") 
                    voice_assistant.start()
                    print(f"[App] ✓ LIA is online | راني واجدة")
                else:
                    print(f"[App] ✗ Failed to initialize LIA")
            
            threading.Thread(target=init_va, daemon=True).start()

    def _init_window(self):
        # Dashboard
        self.dashboard_view = DashboardView()
        self.dashboard_view.setObjectName("dashboardInterface")
        self.dashboard_view.navigate_to.connect(self._navigate_to_tab)
        self.addSubInterface(self.dashboard_view, FIF.LAYOUT, "الرئيسية") # إضافة العربية

        # Lazy load other tabs
        self.chat_lazy = LazyTab(ChatTab, "chatInterface")
        self.planner_lazy = LazyTab(PlannerTab, "plannerInterface")
        self.briefing_view = BriefingView()
        self.briefing_view.setObjectName("briefingInterface")
        self.home_lazy = LazyTab(HomeAutomationTab, "homeInterface")
        self.browser_lazy = LazyTab(BrowserTab, "browserInterface")
        
        # التعديل: إضافة العناوين بالعربية مع الحفاظ على الترتيب الأصلي
        self.addSubInterface(self.chat_lazy, FIF.CHAT, "الدردشة مع LIA")
        self.addSubInterface(self.planner_lazy, FIF.CALENDAR, "المخطط")
        self.addSubInterface(self.briefing_view, FIF.DATE_TIME, "الموجز اليومي")
        self.addSubInterface(self.home_lazy, FIF.HOME, "المنزل الذكي")
        self.addSubInterface(self.browser_lazy, FIF.GLOBE, "البحث الذكي")
        
        # Settings
        self.settings_lazy = LazyTab(SettingsTab, "settingsInterface")
        self.addSubInterface(
            self.settings_lazy, FIF.SETTING, "الإعدادات",
            NavigationItemPosition.BOTTOM
        )

    # ... (بقية الميثودز من _on_wake_word_detected إلى closeEvent تبقى كما هي تماماً) ...

    def _init_background(self):
        """Initialize app status."""
        self.set_status("LIA Ready | راني واجدة")

# ... (نهاية الملف) ...