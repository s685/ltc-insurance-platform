<#
.SYNOPSIS
Automates creating a release branch from main and cherry-picking file contents from develop.

.DESCRIPTION
Fetches latest branches, creates a "release-<date>" branch from main, checks out
specified file paths from develop into the new branch, commits, and optionally pushes.
Includes safety checks, dry-run mode, and clear status output.

.PARAMETER RepoPath
Path to the git repository. Defaults to the current directory.

.PARAMETER Remote
Remote name to use (default: origin).

.PARAMETER ReleasePrefix
Prefix for the release branch (default: release-).

.PARAMETER DateFormat
Date format appended to the release branch (default: yyyyMMdd).

.PARAMETER FilePaths
One or more file paths to copy from develop into the release branch.

.PARAMETER CommitMessage
Commit message for the changes (default: "Release update from develop files").

.PARAMETER Push
If specified, push the new release branch to the remote. Enabled by default.

.PARAMETER NoPush
If specified, do not push the new branch (overrides Push).

.PARAMETER DryRun
If specified, print actions without executing git commands.

.PARAMETER Force
If specified, stashes a dirty working tree to proceed and restores it at the end.

.EXAMPLE
Invoke-GitRelease -FilePaths "src/appsettings.json","src/Config.cs"

.EXAMPLE
Invoke-GitRelease -Remote origin -FilePaths @("web/package.json") -CommitMessage "Update web deps"

.EXAMPLE
Invoke-GitRelease -DryRun -FilePaths @("README.md")
#>
function Invoke-GitRelease {
    [CmdletBinding()]
    param(
        [string]$RepoPath = (Get-Location).Path,
        [string]$Remote = 'origin',
        [string]$ReleasePrefix = 'release-',
        [string]$DateFormat = 'yyyyMMdd',
        [Parameter(Mandatory = $true)]
        [string[]]$FilePaths,
        [string]$CommitMessage = 'Release update from develop files',
        [switch]$Push,
        [switch]$NoPush,
        [switch]$DryRun,
        [switch]$Force
    )

    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    if (-not $PSBoundParameters.ContainsKey('Push')) { $Push = $true }
    if ($NoPush) { $Push = $false }

    function Write-Info([string]$Message) { Write-Host $Message -ForegroundColor Cyan }
    function Write-Step([string]$Message) { Write-Host $Message -ForegroundColor Green }
    function Write-Warn([string]$Message) { Write-Host $Message -ForegroundColor Yellow }
    function Write-Err([string]$Message) { Write-Host $Message -ForegroundColor Red }

    function Invoke-Git([string[]]$Arguments) {
        $display = ($Arguments -join ' ')
        if ($DryRun) {
            Write-Warn "DRY-RUN: git $display"
            return [pscustomobject]@{ ExitCode = 0; Output = ''; Error = '' }
        }
        $output = & git @Arguments 2>&1
        $exit = $LASTEXITCODE
        if ($exit -ne 0) {
            throw "git $display failed with exit code $exit`n$output"
        }
        return [pscustomobject]@{ ExitCode = $exit; Output = $output -join "`n"; Error = '' }
    }

    Write-Step "Validating environment..."
    try { Invoke-Git @('--version') | Out-Null } catch { throw 'git is not available on PATH.' }

    if (-not (Test-Path -LiteralPath $RepoPath)) {
        throw "RepoPath not found: $RepoPath"
    }
    Push-Location -LiteralPath $RepoPath
    try {
        $inside = $false
        try { $inside = (Invoke-Git @('rev-parse','--is-inside-work-tree')).Output.Trim() -eq 'true' } catch { $inside = $false }
        if (-not $inside) { throw 'Current path is not inside a git repository.' }

        $status = (Invoke-Git @('status','--porcelain')).Output
        $isDirty = -not [string]::IsNullOrWhiteSpace(($status -join '').Trim())
        $stashed = $false
        if ($isDirty) {
            if ($Force) {
                Write-Warn 'Working tree is dirty; stashing changes to proceed.'
                Invoke-Git @('stash','push','-u','-m','temp-stash-by-Invoke-GitRelease') | Out-Null
                $stashed = $true
            } else {
                throw 'Working tree has uncommitted changes. Commit/stash or re-run with -Force.'
            }
        }

        Write-Step "Fetching from '$Remote'..."
        Invoke-Git @('fetch','--prune',$Remote) | Out-Null

        Write-Step 'Syncing local main and develop...'
        Invoke-Git @('checkout','main') | Out-Null
        Invoke-Git @('pull','--ff-only',$Remote,'main') | Out-Null
        Invoke-Git @('checkout','develop') | Out-Null
        Invoke-Git @('pull','--ff-only',$Remote,'develop') | Out-Null

        Write-Step 'Creating release branch from main...'
        Invoke-Git @('checkout','main') | Out-Null
        $dateStr = Get-Date -Format $DateFormat
        $baseName = "$ReleasePrefix$dateStr"
        $branchName = $baseName

        function Test-BranchExists([string]$Name) {
            $existsLocal = ($null -ne (& git show-ref --verify "refs/heads/$Name" 2>$null))
            $existsRemote = ($null -ne (& git ls-remote --heads $Remote $Name 2>$null))
            return ($existsLocal -or $existsRemote)
        }

        $suffix = 0
        while (Test-BranchExists $branchName) {
            $suffix++
            $branchName = "$baseName-$suffix"
        }

        Invoke-Git @('checkout','-b',$branchName) | Out-Null

        Write-Step 'Bringing selected files from develop...'
        foreach ($path in $FilePaths) {
            if ([string]::IsNullOrWhiteSpace($path)) { continue }
            Write-Info "Checking out from develop: $path"
            Invoke-Git @('checkout','develop','--',$path) | Out-Null
        }

        $pathsToAdd = @()
        foreach ($path in $FilePaths) { if (-not [string]::IsNullOrWhiteSpace($path)) { $pathsToAdd += $path } }
        if ($pathsToAdd.Count -gt 0) {
            Invoke-Git @('add','--') + $pathsToAdd | Out-Null
        }

        $hasStaged = $true
        try {
            & git diff --cached --quiet
            if ($LASTEXITCODE -eq 0) { $hasStaged = $false }
        } catch { $hasStaged = $false }

        if (-not $hasStaged) {
            Write-Warn 'No staged changes. Nothing to commit.'
        } else {
            Write-Step 'Committing changes...'
            Invoke-Git @('commit','-m',$CommitMessage) | Out-Null
        }

        if ($Push) {
            Write-Step "Pushing branch '$branchName' to '$Remote'..."
            Invoke-Git @('push','-u',$Remote,$branchName) | Out-Null
        } else {
            Write-Warn 'Skipping push (NoPush set).'
        }

        if ($stashed) {
            Write-Step 'Restoring stashed changes...'
            try {
                Invoke-Git @('stash','pop') | Out-Null
            } catch {
                Write-Warn 'Conflicts occurred while applying stashed changes. Please resolve manually.'
            }
        }

        Write-Host ""
        Write-Step 'Done.'
        Write-Host ("Branch: {0}" -f $branchName)
        Write-Host ("Pushed: {0}" -f ($Push -and $hasStaged))
        if ($Push) { Write-Host ("Upstream: {0}/{1}" -f $Remote,$branchName) }
    }
    finally {
        Pop-Location -ErrorAction SilentlyContinue | Out-Null
    }
}

# If the script is executed directly, and parameters are supplied, forward to the function
if ($MyInvocation.InvocationName -ne '.') {
    if ($PSBoundParameters.Count -gt 0 -or $args.Count -gt 0) {
        Invoke-GitRelease @PSBoundParameters @args
    }
}
