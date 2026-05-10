# Extract and Delete - PowerShell version
# Extracts zip files and deletes them after successful extraction
#
# New behavior: if the archive contains a single top-level folder (ignoring
# __MACOSX), the contents are extracted "here" (parent directory) rather
# than creating a subfolder named after the archive.  This prevents nested
# folders when the archive already includes its own container.  In either
# case any __MACOSX directory found after extraction is removed automatically.

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Files
)

# Set window title
$host.UI.RawUI.WindowTitle = "Extract and Delete"

# Use $args if $Files is empty (fallback)
if (($Files.Count -eq 0 -or $null -eq $Files) -and $args.Count -gt 0) {
    $Files = $args
}

# Filter to only archive files
$archives = $Files | Where-Object {
    $_ -match '\.(zip|rar|7z|tar|gz)$'
} | ForEach-Object { Get-Item $_ -ErrorAction SilentlyContinue } | Where-Object { $_ }

if ($archives.Count -eq 0) {
    Write-Host ""
    Write-Host "========================================"
    Write-Host " No archive files selected!"
    Write-Host "========================================"
    Write-Host ""
    Read-Host "Press Enter to close"
    exit
}

# Display header
Clear-Host
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Extract and Delete - Processing $($archives.Count) file(s)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Counters
$current = 0
$success = 0
$failed = 0

# Process each archive
foreach ($archive in $archives) {
    $current++

    # Determine output folder based on archive contents
    $7zipPath = "${env:ProgramFiles}\7-Zip\7z.exe"
    if (-not (Test-Path $7zipPath)) {
        Write-Host "[$current/$($archives.Count)] Extracting: " -NoNewline
        Write-Host $archive.Name -ForegroundColor Yellow
        Write-Host "           ERROR - 7-Zip not found" -ForegroundColor Red
        $failed++
        Write-Host ""
        continue
    }

    # list paths inside archive using 7z and parse for top-level directories
    $list = & $7zipPath l -slt """$($archive.FullName)""" 2>&1
    $paths = $list | ForEach-Object {
        if ($_ -like 'Path = *') { $_ -replace '^Path = ', '' }
    }
    $rootNames = @()
    foreach ($p in $paths) {
        if ([string]::IsNullOrWhiteSpace($p)) { continue }
        # skip the archive file path itself (7z includes it in -slt output)
        if ($p -ieq $archive.FullName) { continue }
        # split on slash or backslash
        $first = ($p -split '[\\/]+')[0]
        if ($first -and $first -ne '__MACOSX') {
            $rootNames += $first
        }
    }
    $rootNames = $rootNames | Sort-Object -Unique

    # decide extraction location
    $extractHere = $false
    if ($rootNames.Count -eq 1) {
        $extractHere = $true
    }

    if ($extractHere) {
        $outputFolder = $archive.DirectoryName
        Write-Host "[$current/$($archives.Count)] Extracting (flattened): " -NoNewline
        Write-Host $archive.Name -ForegroundColor Yellow
    } else {
        $outputFolder = Join-Path $archive.DirectoryName $archive.BaseName
        Write-Host "[$current/$($archives.Count)] Extracting into folder: " -NoNewline
        Write-Host $archive.Name -ForegroundColor Yellow
    }


    if (-not (Test-Path $7zipPath)) {
        Write-Host "           ERROR - 7-Zip not found" -ForegroundColor Red
        $failed++
        Write-Host ""
        continue
    }

    # Run 7-Zip extraction
    $process = Start-Process -FilePath $7zipPath -ArgumentList "x `"$($archive.FullName)`" -o`"$outputFolder\`" -y" -Wait -PassThru -WindowStyle Hidden

    if ($process.ExitCode -eq 0) {
        # Extraction succeeded; remove __MACOSX if present
        $macDir = Join-Path $outputFolder '__MACOSX'
        if (Test-Path $macDir) {
            try {
                Remove-Item $macDir -Recurse -Force -ErrorAction Stop
                Write-Host "           Removed __MACOSX directory" -ForegroundColor Gray
            } catch {
                Write-Host "           WARNING - could not remove __MACOSX" -ForegroundColor Yellow
            }
        }

        # Now try to delete the original archive
        try {
            Remove-Item $archive.FullName -Force -ErrorAction Stop
            Write-Host "           SUCCESS - Archive deleted" -ForegroundColor Green
            $success++
        }
        catch {
            Write-Host "           WARNING - Extracted but could not delete" -ForegroundColor Yellow
            $success++
        }
    }
    else {
        Write-Host "           FAILED - Archive NOT deleted" -ForegroundColor Red
        $failed++
    }

    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Total:   $($archives.Count)"
Write-Host " Success: " -NoNewline
Write-Host $success -ForegroundColor Green
Write-Host " Failed:  " -NoNewline
Write-Host $failed -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Auto-close after 3 seconds
Write-Host "Closing in 3 seconds..." -ForegroundColor Gray
Start-Sleep -Seconds 3
