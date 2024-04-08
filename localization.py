import typing as t
import json
import lightbulb


class MissingLocaleException(BaseException):
    pass


class Localizer:
    __data: t.Dict[str, t.Dict[str, str]] = {}
    __default: str

    def __init__(
        self, langs: t.List[str], default: str
    ):
        self.__default = default

        for i in langs:
            with open(f"./localization/{i}.json") as fd:
                lang_data = t.cast(t.Dict[str, str], json.load(fd))
                self.__data[i] = lang_data

    def get_text(self, locale: t.Union[str, lightbulb.Context], text_id: str):
        if isinstance(locale, lightbulb.Context):
            ctx = locale

            if ctx.interaction:
                locale = ctx.interaction.locale
            else:
                locale = self.__default

        texts = self.__data.get(locale)

        if not texts:
            locale = self.__default
            texts = self.__data.get(locale)

        if not texts:
            raise MissingLocaleException(f"The locale {locale} is not available.")

        text = texts.get(text_id)

        if not text:
            raise MissingLocaleException(
                f"A text with the id {text_id} is not present in locale {locale}"
            )

        return text
