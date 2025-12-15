import os
import re
import sys
import subprocess

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif", ".webp")

def rename_images(root_folder):
    for folder_path, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith(IMAGE_EXTS) and " " in filename:
                old_path = os.path.join(folder_path, filename)
                new_name = filename.replace(" ", "_")
                new_path = os.path.join(folder_path, new_name)

                if old_path != new_path:
                    os.rename(old_path, new_path)
                    print(f"✅ Renamed image: {old_path} → {new_path}")

def update_markdown_links(root_folder):
    """
    所有 Obsidian 圖片語法：
    ![[xxx.png]]
    ![[images/xxx.png]]
    ![[xxx.png|300]]
    ![[folder/xxx.png]]
    → ![](images/xxx.png)
    """
    pattern = re.compile(r'!\[\[([^\]|]+)(\|[^\]]+)?\]\]')

    for folder_path, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if not filename.endswith(".md"):
                continue

            md_path = os.path.join(folder_path, filename)

            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()

            matches = pattern.findall(content)
            if not matches:
                continue

            for raw_path, _ in matches:
                image_name = os.path.basename(raw_path).replace(" ", "_")
                new_md = f"![](images/{image_name})"

                content = re.sub(
                    r'!\[\[' + re.escape(raw_path) + r'(\|[^\]]+)?\]\]',
                    new_md,
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

    print("\n🎉 所有圖片已統一轉為 images/xxx 的 GitHub Markdown 格式！")

if __name__ == "__main__":
    main()
