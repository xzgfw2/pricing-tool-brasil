import os
import gettext
from typing import Optional

# Global variables to track current translation state
_current_lang: Optional[str] = None
_translation: Optional[gettext.GNUTranslations] = None

def setup_translations(lang: str = "pt_BR") -> gettext.GNUTranslations.gettext:
    """
    Configura a tradução para o idioma especificado.
    """
    global _current_lang, _translation

    if lang == _current_lang and _translation:
        return _translation.gettext

    print(f"Setting up translations for language: {lang}")

    # Obtém o diretório base do aplicativo
    base_dir = os.path.dirname(os.path.abspath(__file__))
    locale_dir = os.path.join(base_dir, 'locales')

    try:
        _translation = gettext.translation('messages', localedir=locale_dir, languages=[lang])
        _current_lang = lang

        print("_translation")
        print(_translation)

        print("_current_lang")
        print(_current_lang)

    except FileNotFoundError:
        print(f"Translation file not found for language: {lang}. Using default.")
        _translation = gettext.NullTranslations()
        _current_lang = lang  # Mantém a linguagem solicitada mesmo sem tradução disponível.

    return _translation.gettext

def update_language(lang: str) -> None:
    """
    Atualiza o idioma da aplicação.
    """
    global _
    _ = setup_translations(lang)  # Atualiza a função de tradução global

# Inicializa o tradutor global
_ = setup_translations()
