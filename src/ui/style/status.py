def status_to_color(status_text, colors):
    if "一致" in status_text:
        return "gray"
    if "差异" in status_text:
        return colors.get("warning")
    return colors.get("success")

