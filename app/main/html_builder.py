"""
BUILD_HTML MODULE

module used to build html to sedn to clients.
"""


def build_text_tag(tag, message):
    """
    Helper method to build a basic paragraph tag html object to send
    :param message: the message to have inside the paragraph tags
    :return:
    """

    return f"<{tag}>{message}</{tag}>"

