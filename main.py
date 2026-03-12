"""MTK Studio -- Entry Point"""
import webview
from api import Api


def main():
    api = Api()
    window = webview.create_window(
        'MTK Studio',
        'ui/index.html',
        js_api=api,
        width=1440,
        height=900,
        min_size=(1024, 700),
        resizable=True
    )
    api.set_window(window)
    webview.start(debug=True)


if __name__ == '__main__':
    main()
