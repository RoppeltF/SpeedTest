from win11toast import toast

class WindowsToastNotifier:
    def __init__(self, default_title="System Alert"):
        self.default_title = default_title

    def send(self, title=None, message=""):
        try:
            display_title = title if title else self.default_title
            
            _ = toast(
                title=display_title,
                body=message,
                # icon= r"icon.png" 
            )
            return True
        except Exception as e:
            #print(f"[WindowsToastNotifier Error]: {e}", file=sys.stderr)
            return False


