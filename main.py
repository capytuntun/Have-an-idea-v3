import os
import re
import sys
import subprocess

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp")

def rename_images(root_folder):
    for folder_path, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if " " in filename and filename.lower().endswith(IMAGE_EXTS):
                new_name = filename.replace(" ", "_")
                old_path = os.path.join(folder_path, filename)
                new_path = os.path.join(folder_path, new_name)

                if old_path != new_path:
                    os.rename(old_path, new_path)
                    print(f"✅ Renamed image: {old_path} → {new_path}")

def update_markdown_links(root_folder):
    """
    支援：
    ![[image.png]]
    ![[folder/image.png]]
    ![[image.png|300]]
    """
    obsidian_img_pattern = re.compile(r'!\[\[([^\]|]+)(\|[^\]]+)?\]\]')

    for folder_path, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if not filename.endswith(".md"):
                continue

            md_path = os.path.join(folder_path, filename)
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()

            matches = obsidian_img_pattern.findall(content)
            if not matches:
                continue

            for img_path, _ in matches:
                clean_path = img_path.replace(" ", "_")
                old = f"![[{img_path}]]"
                new = f"![]({clean_path})"

                # 處理有 |300 這種尺寸的
                content = re.sub(
                    r'!\[\[' + re.escape(img_path) + r'(\|[^\]]+)?\]\]',
                    new,
                    content
                )

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"✏️ Updated Markdown: {md_path}")

def git_commit_and_push(root_folder, commit_msg):
    try:
        subprocess.run(["git", "-C", root_folder, "add", "."], check=True)
        subprocess.run(["git", "-C", root_folder, "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "-C", root_folder, "push"], check=True)
        print("🚀 Git commit & push 成功！")
    except subprocess.CalledProcessError as e:
        print("❌ Git 操作失敗：", e)

def main():
    if len(sys.argv) < 3:
        print("❌ 使用方式: python main.py <資料夾路徑> <commit message>")
        sys.exit(1)

    root = sys.argv[1]
    commit_msg = sys.argv[2]

    if not os.path.isdir(root):
        print(f"❌ 找不到資料夾：{root}")
        sys.exit(1)

    rename_images(root)
    update_markdown_links(root)
    git_commit_and_push(root, commit_msg)

    print("\n🎉 所有 Obsidian 圖片已成功轉為 GitHub Markdown！")

if __name__ == "__main__":
    main()
