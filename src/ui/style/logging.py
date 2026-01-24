def get_log_icon_and_color(log_type, colors):
    color = None
    icon = ""

    if log_type == "error":
        color = colors.get("danger")
        icon = "❌ "
    elif log_type == "success":
        color = colors.get("success")
        icon = "✅ "
    elif log_type == "dir":
        color = colors.get("primary")
        icon = "📁 "
    elif log_type == "file_start":
        icon = "⬇️ "

    return icon, color

