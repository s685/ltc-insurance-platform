#!/usr/bin/env bash
set -euo pipefail

# -----------------------------------------------------------------------------
# Compare specific folders between two git branches and report differences
# -----------------------------------------------------------------------------
# Usage examples:
#   ./scripts/compare-branches.sh --folders "frontend" "backend"
#   ./scripts/compare-branches.sh --branch1 main --branch2 release --folders "frontend"
#   ./scripts/compare-branches.sh --branch1 main --branch2 release --folders "frontend" "backend" --summary-only
# -----------------------------------------------------------------------------

BRANCH1="main"
BRANCH2="release"
FOLDERS=()
SUMMARY_ONLY=0
SHOW_CONTENT=1
COLOR=1

log_info(){ [[ $COLOR -eq 1 ]] && echo -e "\033[36m$*\033[0m" || echo "$*"; }
log_step(){ [[ $COLOR -eq 1 ]] && echo -e "\033[32m$*\033[0m" || echo "$*"; }
log_warn(){ [[ $COLOR -eq 1 ]] && echo -e "\033[33m$*\033[0m" || echo "$*"; }
log_err(){ [[ $COLOR -eq 1 ]] && echo -e "\033[31m$*\033[0m" 1>&2 || echo "$*" 1>&2; }
log_diff(){ [[ $COLOR -eq 1 ]] && echo -e "\033[35m$*\033[0m" || echo "$*"; }

usage(){
  cat <<EOF
Usage: $0 [options] --folders <folder1> [folder2 ...]

Compare specific folders between two git branches and report differences.

Options:
  --branch1 <name>          First branch to compare (default: main)
  --branch2 <name>          Second branch to compare (default: release)
  --folders <paths...>      One or more folder paths to compare (required)
  --summary-only            Only show summary, not file content diffs
  --no-color                Disable colored output
  -h, --help                Show this help

Examples:
  $0 --folders frontend backend
  $0 --branch1 develop --branch2 release --folders frontend --summary-only
  $0 --folders scripts sql_scripts
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch1) BRANCH1="$2"; shift 2;;
    --branch2) BRANCH2="$2"; shift 2;;
    --folders)
      shift
      while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do
        FOLDERS+=("$1")
        shift
      done
      ;;
    --summary-only) SUMMARY_ONLY=1; shift;;
    --no-color) COLOR=0; shift;;
    -h|--help) usage; exit 0;;
    *) log_err "Unknown option: $1"; usage; exit 1;;
  esac
done

if [[ ${#FOLDERS[@]} -eq 0 ]]; then
  log_err "--folders is required with at least one folder path"
  usage
  exit 1
fi

# Validate git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  log_err "Not inside a git repository"
  exit 1
fi

# Validate branches exist
if ! git show-ref --verify --quiet "refs/heads/$BRANCH1"; then
  log_err "Branch '$BRANCH1' does not exist locally"
  exit 1
fi

if ! git show-ref --verify --quiet "refs/heads/$BRANCH2"; then
  log_err "Branch '$BRANCH2' does not exist locally"
  log_warn "Attempting to fetch from remote..."
  if git fetch origin "$BRANCH2:$BRANCH2" 2>/dev/null; then
    log_step "Fetched $BRANCH2 from remote"
  else
    log_err "Branch '$BRANCH2' not found in remote either"
    exit 1
  fi
fi

log_step "Comparing branches: $BRANCH1 ↔ $BRANCH2"
echo "Folders to compare: ${FOLDERS[*]}"
echo ""

TOTAL_DIFFS=0
TOTAL_FILES=0
DIFFERENT_FILES=()
NEW_FILES=()
DELETED_FILES=()
MODIFIED_FILES=()

for folder in "${FOLDERS[@]}"; do
  [[ -z "$folder" ]] && continue
  
  log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  log_info "📁 Folder: $folder"
  log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  # Check if folder exists in either branch
  folder_exists_branch1=0
  folder_exists_branch2=0
  
  if git ls-tree -r --name-only "$BRANCH1" | grep -q "^${folder%/}/"; then
    folder_exists_branch1=1
  fi
  
  if git ls-tree -r --name-only "$BRANCH2" | grep -q "^${folder%/}/"; then
    folder_exists_branch2=1
  fi
  
  if [[ $folder_exists_branch1 -eq 0 && $folder_exists_branch2 -eq 0 ]]; then
    log_warn "  Folder does not exist in either branch"
    echo ""
    continue
  fi
  
  if [[ $folder_exists_branch1 -eq 0 ]]; then
    log_warn "  Folder only exists in $BRANCH2 (new folder)"
    echo ""
    continue
  fi
  
  if [[ $folder_exists_branch2 -eq 0 ]]; then
    log_warn "  Folder only exists in $BRANCH1 (deleted in $BRANCH2)"
    echo ""
    continue
  fi
  
  # Get all files in folder from both branches
  files_branch1=$(git ls-tree -r --name-only "$BRANCH1" | grep "^${folder%/}/" || true)
  files_branch2=$(git ls-tree -r --name-only "$BRANCH2" | grep "^${folder%/}/" || true)
  
  # Combine and get unique files
  all_files=$(echo -e "$files_branch1\n$files_branch2" | sort -u)
  
  folder_diff_count=0
  folder_total_count=0
  
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    folder_total_count=$((folder_total_count + 1))
    TOTAL_FILES=$((TOTAL_FILES + 1))
    
    # Check if file exists in both branches
    exists_b1=0
    exists_b2=0
    
    echo "$files_branch1" | grep -Fxq "$file" && exists_b1=1 || true
    echo "$files_branch2" | grep -Fxq "$file" && exists_b2=1 || true
    
    # New file in branch2
    if [[ $exists_b1 -eq 0 && $exists_b2 -eq 1 ]]; then
      NEW_FILES+=("$file")
      folder_diff_count=$((folder_diff_count + 1))
      TOTAL_DIFFS=$((TOTAL_DIFFS + 1))
      log_diff "  ✨ NEW: $file (only in $BRANCH2)"
      continue
    fi
    
    # Deleted file in branch2
    if [[ $exists_b1 -eq 1 && $exists_b2 -eq 0 ]]; then
      DELETED_FILES+=("$file")
      folder_diff_count=$((folder_diff_count + 1))
      TOTAL_DIFFS=$((TOTAL_DIFFS + 1))
      log_diff "  ❌ DELETED: $file (only in $BRANCH1)"
      continue
    fi
    
    # Compare file content
    if git diff --quiet "$BRANCH1" "$BRANCH2" -- "$file" 2>/dev/null; then
      # Files are identical (or git diff doesn't show output)
      continue
    else
      # Files differ
      MODIFIED_FILES+=("$file")
      folder_diff_count=$((folder_diff_count + 1))
      TOTAL_DIFFS=$((TOTAL_DIFFS + 1))
      
      if [[ $SUMMARY_ONLY -eq 0 ]]; then
        log_diff "  🔄 MODIFIED: $file"
        echo ""
        if [[ $SHOW_CONTENT -eq 1 ]]; then
          echo "    ┌─ Diff:"
          git diff --stat "$BRANCH1" "$BRANCH2" -- "$file" | sed 's/^/    │ /' || true
          echo ""
          log_info "    Content diff:"
          git diff "$BRANCH1" "$BRANCH2" -- "$file" | head -n 50 | sed 's/^/    │ /' || true
          if [[ $(git diff "$BRANCH1" "$BRANCH2" -- "$file" | wc -l) -gt 50 ]]; then
            echo "    │ ... (diff truncated, use 'git diff $BRANCH1 $BRANCH2 -- $file' for full diff)"
          fi
          echo ""
        fi
      else
        log_diff "  🔄 MODIFIED: $file"
      fi
    fi
  done <<< "$all_files"
  
  if [[ $folder_diff_count -eq 0 ]]; then
    log_step "  ✅ No differences found in this folder"
  else
    log_warn "  📊 Found $folder_diff_count difference(s) out of $folder_total_count file(s)"
  fi
  
  echo ""
done

# Summary
log_step "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "📊 SUMMARY"
log_step "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Branches compared: $BRANCH1 ↔ $BRANCH2"
echo "Total files scanned: $TOTAL_FILES"
echo "Total differences: $TOTAL_DIFFS"
echo ""

if [[ ${#NEW_FILES[@]} -gt 0 ]]; then
  log_info "✨ New files in $BRANCH2 (${#NEW_FILES[@]}):"
  for f in "${NEW_FILES[@]}"; do
    echo "    + $f"
  done
  echo ""
fi

if [[ ${#DELETED_FILES[@]} -gt 0 ]]; then
  log_warn "❌ Deleted files from $BRANCH1 (${#DELETED_FILES[@]}):"
  for f in "${DELETED_FILES[@]}"; do
    echo "    - $f"
  done
  echo ""
fi

if [[ ${#MODIFIED_FILES[@]} -gt 0 ]]; then
  log_diff "🔄 Modified files (${#MODIFIED_FILES[@]}):"
  for f in "${MODIFIED_FILES[@]}"; do
    echo "    ~ $f"
  done
  echo ""
fi

if [[ $TOTAL_DIFFS -eq 0 ]]; then
  log_step "✅ No differences found! Folders are identical between branches."
  exit 0
else
  log_warn "⚠️  Differences detected!"
  exit 1
fi

