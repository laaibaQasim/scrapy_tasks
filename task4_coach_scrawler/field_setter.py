import json
import re


class ResponseHolder:
    __slots__ = "response"

    @staticmethod
    def set_response(response):
        ResponseHolder.response = response


class ItemSetter:
    def __init__(self):
        self.fields = [
            Skus(),
            Name(),
            Category(),
            Description(),
            ImageUrl(),
            Price(),
            Currency(),
        ]

    def set_fields(self):
        for field in self.fields:
            field.set_value()

    def get_fields(self):
        field_values = {}

        for field in self.fields:
            key, value = field.get_value()
            field_values[key] = value

        return field_values


class Field:
    def __init__(self, get_value_func=None):
        self.response = ResponseHolder.response
        self.get_value_func = get_value_func
        self.value = None

    def set_value(self):
        self.value = self.get_value_func(self.response)

    def get_value(self):
        return self.__class__.__name__, self.value


class Skus(Field):
    def set_value(self):
        self.value = []
        for value in self.get_skus():
            self.value.append(value)

        if not self.value:
            self.value = "Not Applicable"

    def find_sku_dict(self, text):
        start_index = text.find('"sku":')
        if start_index == -1:
            return None

        open_brace_index = text.find("{", start_index + 5)
        if open_brace_index == -1:
            return None

        close_brace_index = text.find("}", open_brace_index)
        if close_brace_index == -1:
            return None

        return text[open_brace_index: close_brace_index + 1]

    def get_skus(self):
        script_text = self.response.xpath(
            '//script[contains(text(), "Magento_Swatches/js/swatch-renderer")]//text()'
        ).get()

        if not script_text:
            return "Not Applicable"

        sku_dict = json.loads(self.find_sku_dict(script_text))

        for key, value in sku_dict.items():
            yield value


class Name(Field):
    def __init__(self):
        super().__init__(
            get_value_func=lambda response: self.response.css(
                "h1.page-title span::text"
            ).get()
        )


class Category(Field):
    def set_value(self):
        ecomm_category_match = re.search(
            r'"ecomm_category":"([^"]+)"', self.response.text
        )
        self.value = (
            lambda match: match.group(1).replace("/", "").replace("\\", ",")
            if match
            else None
        )(ecomm_category_match)


class Description(Field):
    def __init__(self):
        super().__init__(
            get_value_func=lambda response: self.response.css(
                "div.product.attribute.description div.value li::text"
            ).getall()
        )


class ImageUrl(Field):
    def __init__(self):
        super().__init__(
            get_value_func=lambda response: response.css(
                'img[alt="main product photo"]::attr(src)'
            ).get()
        )


class Price(Field):
    def __init__(self):
        super().__init__(
            get_value_func=lambda response: (
                "Not Applicable"
                if (span := response.css(".product-info-price" " .price::text").get())
                is None
                else span.split("\xa0", 1)[1]
            )
        )


class Currency(Field):
    def __init__(self):
        super().__init__(
            get_value_func=lambda response: (
                "Not Applicable"
                if (span := response.css(".product-info-price" " .price::text").get())
                is None
                else span.split("\xa0", 1)[0]
            )
        )
