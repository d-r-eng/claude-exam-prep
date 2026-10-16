# Rebuilds installer\claude-exam-prep-code.zip from the LICENSE file and the
# current contents of src\ (Windows PowerShell 5.1+ / PowerShell 7). Replaces the existing zip.
#
# Left out of the zip (personal data and build junk): __pycache__, *.pyc,
# .exam-app\, settings.local.json, fexam-/pexam-performance.json,
# fexam-scorereport.json, workspace.md, ccar-f_p2.html/.json
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$Repo    = Split-Path -Parent $PSScriptRoot
$Src     = Join-Path $Repo 'src'
$License = Join-Path $Repo 'LICENSE'
$Out     = Join-Path $Repo 'installer\claude-exam-prep-code.zip'
if (-not (Test-Path $Src -PathType Container)) { throw "$Src not found." }
if (-not (Test-Path $License -PathType Leaf))  { throw "$License not found." }

$Skip = @('__pycache__', '.exam-app', 'settings.local.json', 'fexam-performance.json',
          'pexam-performance.json', 'fexam-scorereport.json', 'workspace.md',
          'ccar-f_p2.html', 'ccar-f_p2.json')

function Get-Entries([string]$Dir, [string]$Prefix) {
    foreach ($item in (Get-ChildItem -LiteralPath $Dir -Force | Sort-Object Name)) {
        if ($Skip -contains $item.Name) { continue }
        if ($item.PSIsContainer) { Get-Entries $item.FullName "$Prefix$($item.Name)/" }
        elseif ($item.Extension -ne '.pyc') { [pscustomobject]@{ Full = $item.FullName; Name = "$Prefix$($item.Name)" } }
    }
}

$entries = @([pscustomobject]@{ Full = $License; Name = 'LICENSE' }) + @(Get-Entries $Src '')
$tmp = "$Out.tmp"
if (Test-Path $tmp) { Remove-Item -Force $tmp }
$zip = [System.IO.Compression.ZipFile]::Open($tmp, 'Create')
try {
    foreach ($e in $entries) {
        # Entry names use forward slashes so the zip extracts correctly on every OS.
        [void][System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $e.Full, $e.Name, 'Optimal')
    }
} finally { $zip.Dispose() }
Move-Item -Force $tmp $Out
Write-Host ("Wrote {0} ({1} files, {2} bytes)" -f $Out, $entries.Count, (Get-Item $Out).Length)
