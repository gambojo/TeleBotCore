import html
from typing import List

class HTMLBuilder:
    """
    Построитель HTML-текста для сообщений Telegram
    Параметры: не принимает параметров при создании
    Возвращает: экземпляр HTMLBuilder
    Пример: builder = HTMLBuilder()
    """

    def __init__(self):
        self.lines: list[str] = []

    def _escape(self, text: str | None) -> str:
        if not text:
            return "—"
        return html.escape(str(text))

    def title(self, text: str, emoji: str = "📌") -> "HTMLBuilder":
        '''
        HTMLBuilder().title("Профиль").build()
        <b>📌 Профиль</b>
        '''
        self.lines.append(f"<b>{emoji} {self._escape(text)}</b>")
        return self

    def field(self, label: str, value: str | None, emoji: str = "▪️") -> "HTMLBuilder":
        '''
        HTMLBuilder().field("Имя", "Гамид").build()
        ▪️ <b>Имя:</b> <code>Гамид</code>
        '''
        self.lines.append(f"{emoji} <b>{self._escape(label)}:</b> <code>{self._escape(value)}</code>")
        return self

    def list(self, items: List[str], emoji: str = "•") -> "HTMLBuilder":
        '''
        HTMLBuilder().list(["Услуга A", "Услуга B"]).build()
        • Услуга A
        • Услуга B
        '''
        for item in items:
            self.lines.append(f"{emoji} {self._escape(item)}")
        return self

    def link(self, label: str, url: str, emoji: str = "🔗") -> "HTMLBuilder":
        '''
        HTMLBuilder().link("Справка", "https://example.com/help").build()
        🔗 <a href="https://example.com/help">Справка</a>
        '''
        self.lines.append(f'{emoji} <a href="{html.escape(url)}">{self._escape(label)}</a>')
        return self

    def note(self, text: str, emoji: str = "💬") -> "HTMLBuilder":
        '''
        HTMLBuilder().note("Обратитесь к администратору").build()
        💬 <i>Обратитесь к администратору</i>
        '''
        self.lines.append(f"{emoji} <i>{self._escape(text)}</i>")
        return self

    def blank(self) -> "HTMLBuilder":
        self.lines.append("")
        return self

    def code_block(self, code: str, language: str = "") -> "HTMLBuilder":
        '''
        HTMLBuilder().code_block("print('Hello')").build()
        <pre><code>print('Hello')</code></pre>
        '''
        escaped = html.escape(code)
        self.lines.append(f"<pre><code>{escaped}</code></pre>")
        return self

    def quote(self, text: str) -> "HTMLBuilder":
        '''
        HTMLBuilder().quote("Это важно").build()
        • Это важно
        '''
        self.lines.append(f"• {self._escape(text)}")
        return self

    def render_user(self, user) -> "HTMLBuilder":
        return (
            self.title("Профиль:", "👤")
                .field("Имя", user.first_name)
                .field("Id", user.telegram_id)
                .field("Роль", user.role)
        )

    def build(self) -> str:
        """
        Собирает все добавленные элементы в готовый HTML-текст
        Возвращает: str - HTML-текст для отправки в Telegram
        Пример: html_text = builder.title("Заголовок").field("Поле", "значение").build()
        """

        return "\n".join(self.lines)
