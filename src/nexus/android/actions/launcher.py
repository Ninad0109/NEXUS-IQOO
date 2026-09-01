"""Android App Registry and Launcher."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AppInfo:
    name: str
    package: str
    main_activity: Optional[str] = None
    aliases: list[str] = None


class AppLauncher:
    """Manages app package resolution and intent generation."""

    KNOWN_APPS: dict[str, AppInfo] = {
        "whatsapp": AppInfo(
            name="WhatsApp",
            package="com.whatsapp",
            main_activity="com.whatsapp.Main",
            aliases=["wa", "whats app", "watsapp"],
        ),
        "gmail": AppInfo(
            name="Gmail",
            package="com.google.android.gm",
            main_activity="com.google.android.gm.ConversationListActivityGmail",
            aliases=["mail", "email", "google mail"],
        ),
        "chrome": AppInfo(
            name="Chrome",
            package="com.android.chrome",
            main_activity="com.google.android.apps.chrome.Main",
            aliases=["google chrome", "browser", "web browser", "internet"],
        ),
        "settings": AppInfo(
            name="Settings",
            package="com.android.settings",
            main_activity="com.android.settings.Settings",
            aliases=["phone settings", "device settings"],
        ),
        "calculator": AppInfo(
            name="Calculator",
            package="com.google.android.calculator",
            aliases=["calc", "vivo calculator", "com.vivo.calculator"],
        ),
        "camera": AppInfo(
            name="Camera",
            package="com.android.camera2",
            aliases=["vivo camera", "com.vivo.camera"],
        ),
        "clock": AppInfo(
            name="Clock",
            package="com.google.android.deskclock",
            aliases=["alarm", "timer", "vivo clock"],
        ),
    }

    def resolve_package(self, app_name_or_package: str) -> str:
        """Resolves natural language name or alias to Android package name."""
        query = app_name_or_package.strip().lower()
        
        # If it looks like a package name already
        if "." in query and not query.endswith("."):
            return app_name_or_package.strip()

        # Exact key match
        if query in self.KNOWN_APPS:
            return self.KNOWN_APPS[query].package

        # Alias match
        for key, info in self.KNOWN_APPS.items():
            if info.name.lower() == query:
                return info.package
            if info.aliases:
                for alias in info.aliases:
                    if alias.lower() == query or alias.lower() in query:
                        return info.package

        return app_name_or_package.strip()

    def get_app_name(self, package: str) -> str:
        """Converts package name back to friendly app name."""
        for key, info in self.KNOWN_APPS.items():
            if info.package == package:
                return info.name
        return package.split(".")[-1].capitalize()
