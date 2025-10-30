#!/usr/bin/env bash
set -euo pipefail

# -----------------------------------------------------------------------------
# Automates creating a release branch from main and cherry-picking file contents
# from develop by checking out file paths from develop into a new branch.
# Includes safety checks, dry-run mode, and clear status output.
# -----------------------------------------------------------------------------
# Usage examples:
#   ./scripts/invoke-git-release.sh --files README.md frontend/streamlit_app.py
#   ./scripts/invoke-git-release.sh --remote origin --message "Update web deps" --files web/package.json
#   ./scripts/invoke-git-release.sh --dry-run --files README.md
# -----------------------------------------------------------------------------

REPO_PATH="$(pwd)"
REMOTE="origin"
RELEASE_PREFIX="release-"
DATE_FORMAT="+%Y%m%d" # date(1) format string
COMMIT_MESSAGE="Release update from develop files"
PUSH=1
DRY_RUN=0
FORCE=0
NO_PUSH=0
FILES=()

log_info(){ echo -e "\033[36m$*\033[0m"; }
log_step(){ echo -e "\033[32m$*\033[0m"; }
log_warn(){ echo -e "\033[33m$*\033[0m"; }
log_err(){ echo -e "\033[31m$*\033[0m" 1>&2; }

run(){
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log_warn "DRY-RUN: $*"
  else
    eval "$@"
  fi
}

usage(){
  cat <<EOF
Usage: $0 [options] --files <path1> [path2 ...]

Options:
  --repo <path>            Path to git repo (default: current directory)
  --remote <name>          Remote name (default: origin)
  --prefix <string>        Release branch prefix (default: release-)
  --date-format <fmt>      date(1) format (default: +%Y%m%d)
  --files <paths...>       One or more file paths to copy from develop
  --message <text>         Commit message (default provided)
  --push                   Push new branch (default: enabled)
  --no-push                Do not push (overrides --push)
  --dry-run                Print actions without executing git commands
  --force                  Stash dirty worktree to proceed, restore after
  -h, --help               Show this help
EOF
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO_PATH="$2"; shift 2;;
    --remote) REMOTE="$2"; shift 2;;
    --prefix) RELEASE_PREFIX="$2"; shift 2;;
    --date-format) DATE_FORMAT="$2"; shift 2;;
    --files)
      shift
      while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do FILES+=("$1"); shift; done
      ;;
    --message) COMMIT_MESSAGE="$2"; shift 2;;
    --push) PUSH=1; shift;;
    --no-push) NO_PUSH=1; shift;;
    --dry-run) DRY_RUN=1; shift;;
    --force) FORCE=1; shift;;
    -h|--help) usage; exit 0;;
    *) log_err "Unknown option: $1"; usage; exit 1;;
  esac
done

if [[ ${#FILES[@]} -eq 0 ]]; then
  log_err "--files is required with at least one path"
  usage
  exit 1
fi

if [[ $NO_PUSH -eq 1 ]]; then PUSH=0; fi

log_step "Validating environment..."
if ! command -v git >/dev/null 2>&1; then
  log_err "git is not available on PATH."
  exit 1
fi

if [[ ! -d "$REPO_PATH" ]]; then
  log_err "Repo path not found: $REPO_PATH"
  exit 1
fi

cd "$REPO_PATH"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  log_err "Current path is not inside a git repository."
  exit 1
fi

# Worktree cleanliness
is_dirty=0
if [[ -n "$(git status --porcelain)" ]]; then is_dirty=1; fi
stashed=0
if [[ $is_dirty -eq 1 ]]; then
  if [[ $FORCE -eq 1 ]]; then
    log_warn "Working tree is dirty; stashing changes to proceed."
    run "git stash push -u -m temp-stash-by-invoke-git-release >/dev/null"
    stashed=1
  else
    log_err "Working tree has uncommitted changes. Commit/stash or re-run with --force."
    exit 1
  fi
fi

log_step "Fetching from '$REMOTE'..."
run "git fetch --prune $REMOTE"

log_step "Syncing local main and develop..."
run "git checkout main"
run "git pull --ff-only $REMOTE main"
run "git checkout develop"
run "git pull --ff-only $REMOTE develop"

log_step "Creating release branch from main..."
run "git checkout main"
DATE_STR="$(date "$DATE_FORMAT")"
BASE_NAME="${RELEASE_PREFIX}${DATE_STR}"
BRANCH_NAME="$BASE_NAME"

branch_exists(){
  git show-ref --verify --quiet "refs/heads/$1" || git ls-remote --exit-code --heads "$REMOTE" "$1" >/dev/null 2>&1
}

suffix=0
if branch_exists "$BRANCH_NAME"; then
  while branch_exists "$BRANCH_NAME"; do
    suffix=$((suffix+1))
    BRANCH_NAME="${BASE_NAME}-${suffix}"
  done
fi

run "git checkout -b $BRANCH_NAME"

log_step "Bringing selected files from develop..."
for p in "${FILES[@]}"; do
  [[ -z "$p" ]] && continue
  log_info "Checking out from develop: $p"
  run "git checkout develop -- -- '$p'"

done

# Stage changes
if [[ $DRY_RUN -eq 0 ]]; then
  git add -- ${FILES[@]} 2>/dev/null || true
  if git diff --cached --quiet; then
    log_warn "No staged changes. Nothing to commit."
  else
    log_step "Committing changes..."
    git commit -m "$COMMIT_MESSAGE"
  fi
else
  log_warn "DRY-RUN: git add -- ${FILES[*]}"
  log_warn "DRY-RUN: git commit -m '$COMMIT_MESSAGE' (if staged)"
fi

if [[ $PUSH -eq 1 ]]; then
  log_step "Pushing branch '$BRANCH_NAME' to '$REMOTE'..."
  run "git push -u $REMOTE $BRANCH_NAME"
else
  log_warn "Skipping push (--no-push set)."
fi

if [[ $stashed -eq 1 ]]; then
  log_step "Restoring stashed changes..."
  if [[ $DRY_RUN -eq 0 ]]; then
    set +e
    git stash pop
    pop_rc=$?
    set -e
    if [[ $pop_rc -ne 0 ]]; then
      log_warn "Conflicts occurred while applying stashed changes. Please resolve manually."
    fi
  else
    log_warn "DRY-RUN: git stash pop"
  fi
fi

echo ""
log_step "Done."
echo "Branch: $BRANCH_NAME"
echo "Pushed: $([[ $PUSH -eq 1 ]] && echo yes || echo no)"
[[ $PUSH -eq 1 ]] && echo "Upstream: $REMOTE/$BRANCH_NAME" || true
