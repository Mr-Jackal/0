import os
import shutil
import subprocess
import requests

# ─── CONFIG (from GitHub Actions Secrets) ───────────────────────────
SOURCE_OWNER  = os.environ["SOURCE_OWNER"]    # Ns81000
TARGET_OWNER  = os.environ["TARGET_OWNER"]    # Mr-Jackal
TARGET_EMAIL  = os.environ["TARGET_EMAIL"]    # secondary account email
TARGET_TOKEN  = os.environ["TARGET_GH_TOKEN"] # PAT of secondary account

REPOS_FILE    = "repos.txt"
UPLOADED_FILE = "uploaded.txt"
CLONE_DIR     = "/tmp/current_repo"
GITHUB_API    = "https://api.github.com"

headers = {
    "Authorization": f"Bearer {TARGET_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# ─── STEP 1: Find next repo to upload ───────────────────────────────
def get_next_repo():
    with open(REPOS_FILE, "r") as f:
        all_repos = [line.strip() for line in f if line.strip()]

    uploaded = []
    if os.path.exists(UPLOADED_FILE):
        with open(UPLOADED_FILE, "r") as f:
            uploaded = [line.strip() for line in f if line.strip()]

    for repo in all_repos:
        if repo not in uploaded:
            return repo

    return None  # All done

# ─── STEP 2: Fetch source repo metadata ─────────────────────────────
def get_metadata(repo_name):
    url = f"{GITHUB_API}/repos/{SOURCE_OWNER}/{repo_name}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    return {
        "description": data.get("description") or "",
        "homepage":    data.get("homepage") or "",
        "private":     data.get("private", False)
    }

# ─── STEP 3: Clone and strip git history ────────────────────────────
def clone_and_clean(repo_name):
    if os.path.exists(CLONE_DIR):
        shutil.rmtree(CLONE_DIR)

    clone_url = f"https://github.com/{SOURCE_OWNER}/{repo_name}.git"
    subprocess.run(["git", "clone", clone_url, CLONE_DIR], check=True)

    git_dir = os.path.join(CLONE_DIR, ".git")
    if os.path.exists(git_dir):
        shutil.rmtree(git_dir)

    print(f"✅ Cloned and cleaned: {repo_name}")

# ─── STEP 4: Replace username in README ─────────────────────────────
def patch_readme():
    for filename in ["README.md", "readme.md", "Readme.md", "README.MD"]:
        path = os.path.join(CLONE_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            patched = content.replace(SOURCE_OWNER, TARGET_OWNER)

            with open(path, "w", encoding="utf-8") as f:
                f.write(patched)

            print(f"✅ Patched README: '{SOURCE_OWNER}' → '{TARGET_OWNER}'")
            return

    print("ℹ️ No README found, skipping patch")

# ─── STEP 5: Create repo on secondary account ───────────────────────
def create_target_repo(repo_name, description, private):
    url = f"{GITHUB_API}/user/repos"
    payload = {
        "name":        repo_name,
        "description": description,
        "private":     private,
        "auto_init":   False
    }
    r = requests.post(url, json=payload, headers=headers)

    if r.status_code == 422:
        print(f"⚠️ Repo '{repo_name}' already exists on target — will force push")
        return

    r.raise_for_status()
    print(f"✅ Created repo: {TARGET_OWNER}/{repo_name}")

# ─── STEP 6: Push to secondary account ──────────────────────────────
def push_to_target(repo_name):
    remote_url = f"https://{TARGET_OWNER}:{TARGET_TOKEN}@github.com/{TARGET_OWNER}/{repo_name}.git"

    cmds = [
        ["git", "init"],
        ["git", "config", "user.email", TARGET_EMAIL],
        ["git", "config", "user.name",  TARGET_OWNER],
        ["git", "add",    "."],
        ["git", "commit", "-m", "Initial commit"],
        ["git", "branch", "-M", "main"],
        ["git", "remote", "add", "origin", remote_url],
        ["git", "push",   "-u", "origin", "main", "--force"]
    ]

    for cmd in cmds:
        subprocess.run(cmd, cwd=CLONE_DIR, check=True)

    print(f"✅ Pushed to https://github.com/{TARGET_OWNER}/{repo_name}")

# ─── STEP 7: Update description via API ─────────────────────────────
def update_description(repo_name, description, homepage):
    url = f"{GITHUB_API}/repos/{TARGET_OWNER}/{repo_name}"
    payload = {
        "description": description,
        "homepage":    homepage
    }
    r = requests.patch(url, json=payload, headers=headers)
    r.raise_for_status()
    print(f"✅ Description updated: {description or '(empty)'}")

# ─── STEP 8: Mark repo as uploaded ──────────────────────────────────
def mark_uploaded(repo_name):
    with open(UPLOADED_FILE, "a") as f:
        f.write(repo_name + "\n")
    print(f"✅ Marked as uploaded: {repo_name}")

# ─── MAIN ────────────────────────────────────────────────────────────
def main():
    repo = get_next_repo()

    if repo is None:
        print("🎉 All repos have been uploaded! Nothing left to do.")
        return

    print(f"\n🚀 Processing: {SOURCE_OWNER}/{repo} → {TARGET_OWNER}/{repo}\n")

    metadata = get_metadata(repo)
    clone_and_clean(repo)
    patch_readme()
    create_target_repo(repo, metadata["description"], metadata["private"])
    push_to_target(repo)
    update_description(repo, metadata["description"], metadata["homepage"])
    mark_uploaded(repo)

    print(f"\n✅ Done for today: {repo}")

if __name__ == "__main__":
    main()
