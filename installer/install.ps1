# Claude Exam Prep installer (native Windows, PowerShell)
# Extracts claude-exam-prep-code.zip (next to this script) into a new directory
# in the current working directory, runs the tests, then starts the app.
$ErrorActionPreference = 'Stop'

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Zip         = Join-Path $ScriptDir 'claude-exam-prep-code.zip'
$DefaultName = 'claude-exam-prep'

function Fail($msg) { Write-Host "ERROR: $msg" -ForegroundColor Red; exit 1 }

# --- prerequisites (checked before anything is created) ---------------------
# Python: prefer the 'py' launcher, fall back to 'python'. Reject the Microsoft Store stub.
$PyExe = $null; $PyArgs = @()
if (Get-Command py -ErrorAction SilentlyContinue) { $PyExe = 'py'; $PyArgs = @('-3') }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $PyExe = 'python' }
if ($PyExe) {
    & $PyExe @PyArgs --version *> $null
    if ($LASTEXITCODE -ne 0) { $PyExe = $null }
}

$missing = $false
if (-not $PyExe) {
    Write-Host 'Python 3 was not found (or only the Microsoft Store stub is present).'
    Write-Host '  Install it:  winget install Python.Python.3.12   (or https://www.python.org/downloads/)'
    Write-Host '  Then open a new PowerShell window.'
    $missing = $true
}
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host "Claude Code ('claude') was not found on your PATH."
    Write-Host '  Install it from https://claude.ai/code, then run "claude" once to sign in.'
    $missing = $true
}
if ($missing) { Fail 'Install the missing prerequisites above and run this installer again.' }
if (-not (Test-Path $Zip)) { Fail "Cannot find $Zip (it must sit next to install.ps1)." }

# --- ask for directory name -------------------------------------------------
$Name = Read-Host "New directory name [$DefaultName]"
if ([string]::IsNullOrWhiteSpace($Name)) { $Name = $DefaultName }
$Name = $Name.Trim()
if ($Name -match '[\\/:*?"<>|]' -or $Name -eq '.' -or $Name -eq '..') {
    Fail "Enter a plain folder name (no slashes or special characters); it is created in $((Get-Location).Path)."
}
$Target = Join-Path (Get-Location).Path $Name
if (Test-Path $Target) { Fail "$Target already exists. Nothing was changed." }

# --- create and extract -----------------------------------------------------
Write-Host "Creating $Target ..."
New-Item -ItemType Directory -Path $Target | Out-Null
try {
    Expand-Archive -Path $Zip -DestinationPath $Target
} catch {
    Remove-Item -Recurse -Force $Target -ErrorAction SilentlyContinue
    Fail "Extraction failed; removed $Target. $_"
}

# --- verify -----------------------------------------------------------------
Write-Host 'Running tests ...'
Push-Location $Target
try {
    & $PyExe @PyArgs -m unittest discover -s app -p 'test_*.py'
    if ($LASTEXITCODE -ne 0) { Pop-Location; Fail "Tests failed. Files are in $Target but the app was not started." }

    Write-Host ''
    Write-Host "Installed to: $Target"
    Write-Host "Next time:    cd `"$Target`"; python app\serve.py --open"
    Write-Host "Or in Claude Code:  cd `"$Target`"; claude   (then /fexam medium)"
    Write-Host ''
    Write-Host 'Starting the app at http://localhost:8765/practice (Ctrl+C to stop) ...'
    & $PyExe @PyArgs app\serve.py --open
} finally {
    Pop-Location -ErrorAction SilentlyContinue
}
