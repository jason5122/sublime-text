from LSP.plugin import AbstractPlugin, register_plugin, unregister_plugin
from LSP.plugin.core.protocol import DocumentUri
from LSP.plugin.core.typing import Callable


class KotlinJason(AbstractPlugin):
    @classmethod
    def name(cls) -> str:
        return "kotlin-jason"

    def on_open_uri_async(self, uri: DocumentUri, callback: Callable[[str, str, str], None]) -> bool:
        print(uri)
        return False


def plugin_loaded() -> None:
    register_plugin(KotlinJason)


def plugin_unloaded() -> None:
    unregister_plugin(KotlinJason)
