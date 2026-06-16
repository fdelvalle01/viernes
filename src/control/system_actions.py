from __future__ import annotations

import webbrowser


class SystemActions:
    """Safe local OS actions allowed in the MVP."""

    DEFAULT_URL = "https://www.google.com"

    def open_browser(self) -> bool:
        try:
            result = webbrowser.open(self.DEFAULT_URL, new=2, autoraise=True)
            if result:
                print(f"Opening browser: {self.DEFAULT_URL}")
                return True
            else:
                print(f"Failed to open browser: {self.DEFAULT_URL}")
                return False
        except Exception as e:
            print(f"Error opening browser: {e}")
            return False

    def open_default_browser(self) -> bool:
        return self.open_browser()
