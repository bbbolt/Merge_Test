import os
import imgkit
import markdown


# markdown字符串转成image截图
def markdown_to_image(markdown_str: str, image_path: str):
    html = markdown.markdown(markdown_str)

    # 工具路径
    file_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.abspath(os.path.join(file_dir, "..", '..'))
    path_wkimg = os.path.join(path, "static", "tools", "wkhtmltoimage.exe")
    cfg = imgkit.config(wkhtmltoimage=path_wkimg)
    # 3、将字符串转为图片
    imgkit.from_string(html, image_path, config=cfg)
