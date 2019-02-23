class MarkdownInline:
    def __init__(self, content):
        self.content = content

    def __str__(self):
        return self.content


class MarkdownBlock:
    @staticmethod
    def get_ending_whitespace(end):
        if end.endswith("\n\n"):
            return ""
        elif end.endswith("\n"):
            return "\n"
        else:
            return "\n\n"


class MarkdownLeafBlock(MarkdownBlock):
    def __init__(self, content=""):
        self.content = content

    def add(self, inline_content):
        self.content += str(inline_content)

    def build(self, pre_text="", post_text=""):
        return pre_text + self.content + post_text + self.get_ending_whitespace(self.content + post_text)


class MarkdownContainerLine(MarkdownInline):
    def __str__(self):
        return self.content + "\n"

class MarkdownContainerBlock(MarkdownBlock):
    def __init__(self):
        self.items = []

    def add(self, item):
        self.items.append(item)

    def build(self, pre_text="", post_text=""):
        out = []
        for i, item in enumerate(self.items):
            # if we have a list, insert an additional newline at the end of group of ListItems
            if i > 0 and isinstance(self.items[i - 1], MarkdownListItem)\
                    and not isinstance(item, MarkdownListItem):
                out.append("\n")
            out.append(pre_text + str(item) + post_text)
        if len(out) > 0:
            last_item = out[-1]
            if not isinstance(last_item, MarkdownListItem) and not isinstance(self, MarkdownDocument):
                out.append(self.get_ending_whitespace(last_item))
        return "".join(out)


class MarkdownDocument(MarkdownContainerBlock):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return self.build()


class MarkdownStrong(MarkdownInline):
    def __init__(self, content):
        super().__init__(content)

    def __str__(self):
        content = super().__str__()
        leading_whitespace = content[:len(content)-len(content.lstrip())]
        trailing_whitespace = content[len(content.rstrip()):]
        return leading_whitespace + "**" + content.strip() + "**" + trailing_whitespace


class MarkdownItalics(MarkdownInline):
    def __init__(self, content):
        super().__init__(content)

    def __str__(self):
        content = super().__str__()
        leading_whitespace = content[:len(content)-len(content.lstrip())]
        trailing_whitespace = content[len(content.rstrip()):]
        return leading_whitespace + "*" + content.strip() + "*" + trailing_whitespace


class MarkdownLink(MarkdownInline):
    def __init__(self, text, link):
        self.content = self.build(text, link)

    def build(self, text, link):
        link = self.clear_leading_slashes_of_links(link)
        link_builder = list(link)
        escaped = ["(", ")"]
        for i in range(len(link_builder) - 1, -1, -1):
            if link_builder[i] in escaped:
                link_builder.insert(i, '\\')
        return "[" + text + "](" + "".join(link_builder) + ")"

    @staticmethod
    def clear_leading_slashes_of_links(url):
        if len(url) == 0 or url[0] != "/":
            return url
        while url[0] == "/":
            url = url[1:]
        return "https://" + url


class MarkdownHeader(MarkdownLeafBlock):
    def __init__(self, content, header_level=1):
        super().__init__(content)
        self.header_level = header_level

    def __str__(self):
        pre = "#" * self.header_level + " "
        return self.build(pre_text=pre)


class MarkdownParagraph(MarkdownLeafBlock):
    def __str__(self):
        return self.build()


class MarkdownQuotebox(MarkdownContainerBlock):
    def __str__(self):
        return self.build()

    def build(self, pre_text="", post_text=""):
        out = []
        for item in self.items:
            new_item = ""
            for line in str(item).splitlines():
                new_item += "> " + line + "\n"
            out.append(pre_text + str(new_item) + post_text)
        if len(out) > 0:
            last_item = out[-1]
            out.append(self.get_ending_whitespace(last_item))
        return "".join(out)


class MarkdownCodeSpan(MarkdownInline):
    def __str__(self):
        return "``" + self.content + "``"


class MarkdownCodeBlock(MarkdownLeafBlock):
    def __str__(self):
        # modify the content with 4 spaces of indentation
        out = []
        for line in self.content.lstrip().splitlines():
            out.append("    " + line + "\n")
        self.content = "".join(out)
        final = self.build(pre_text="```\n", post_text="```")
        return final

# Reddit specific Table implementation
class MarkdownTable(MarkdownBlock):
    def __init__(self, rows, headers=None):
        self.rows = rows
        if headers:
            self.headers = headers
        else:
            self.headers = []
        # reddit table rows cannot have variable widths
        # the table width here is set to the width of the row with the most items
        self.width = len(self.headers)
        for row in rows:
            rlen = len(row)
            if rlen > self.width:
                self.width = rlen

    def __str__(self):
        return self.build()

    def build(self):
        header_underline = "|" + "-|" * self.width
        header_line = self.divide_row_items(self.headers)
        row_lines = []
        for row in self.rows:
            row_lines.append(self.divide_row_items(row))

        rows_concatenated = "\n".join(row_lines)
        return header_line + "\n" + header_underline + "\n" + rows_concatenated + "\n\n"

    def divide_row_items(self, row):
        output = "|".join(row) + "|" + "|" * (self.width - len(row))
        if len(row) > 0:
            output = "|" + output
        return output


class MarkdownList(MarkdownContainerBlock):
    def __str__(self):
        return self.build("* ", "\n")


class MarkdownListItem(MarkdownContainerLine):
    def __str__(self):
        if len(self.content) > 0 and self.content[-1] != "\n":
            return "* " + self.content + "\n"
        else:
            return "* " + self.content
