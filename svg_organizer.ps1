# SVG File Organizer Script
# Copies all SVG files from PICTURES/TYPE/PROJECT_NAME/SUB_FOLDERS
# to a new organized structure: PROJECTS/PROJECT_NAME/

param(
    [string]$SourcePath = ".\PICTURES",
    [string]$DestinationPath = ".\PROJECTS",
    [switch]$WhatIf,
    [switch]$PreservePath,
    [switch]$CleanNames,
    [int]$MaxNameLength = 50
)

function Clean-FileName {
    param([string]$Name, [int]$MaxLength = 50)
    
    # Clean layer naming - convert to simple numbers
    $Name = $Name -replace '(?i)\s*-?\s*Layer\s+(\d+)', ' $1'
    $Name = $Name -replace '(?i)\s*-?\s*layer\s+(\d+)', ' $1'  
    $Name = $Name -replace '(?i)\s*-?\s*Layer\s+0?(\d)', ' $1'
    
    # Remove marketing patterns
    $Name = $Name -replace '-SVG-PNG-\d+', ''
    $Name = $Name -replace '-SVG-\d+', ''
    $Name = $Name -replace '-PNG-\d+', ''
    $Name = $Name -replace '-EPS-\d+', ''
    $Name = $Name -replace '\-\d{6,}', ''
    $Name = $Name -replace '_\d{6,}', ''
    
    # Remove common words
    $Name = $Name -replace '(?i)\b(Sublimation|Bundle|Template|Graphics?|Elements?)\b', ''
    $Name = $Name -replace '(?i)\b(Quotes?|Papercuts?|Paper\s+Cuts?)\b', ''
    $Name = $Name -replace '(?i)\b(Laser\s+Cut|Cut\s+File|SVG\s+File)\b', ''
    $Name = $Name -replace '(?i)\b(Shadow\s+Box|Light\s+Box|3D)\b', ''
    $Name = $Name -replace '(?i)\b(Layered|MultiLayered|Multi\s+Layered)\b', ''
    
    # Remove timestamps
    $Name = $Name -replace '\.\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d+', ''
    $Name = $Name -replace '-\d{4}-\d{2}-\d{2}', ''
    
    # Remove versions and duplicates
    $Name = $Name -replace '(?i)\s+v\d+$', ''
    $Name = $Name -replace '(?i)\s+Version\s+\d+$', ''
    $Name = $Name -replace '\s+\(\d+\)$', ''
    $Name = $Name -replace '(?i)\s+-\s+Copy$', ''
    
    # Remove weird patterns
    $Name = $Name -replace '\b\d{4}\.m\d{2}\.i\d{3}\.n\d{3}_e\d{2}\b', ''
    $Name = $Name -replace '(?i)\b[a-z]-\d{2}\b', ''
    
    # Clean spacing
    $Name = $Name -replace '\s*-\s*-\s*', ' - '
    $Name = $Name -replace '\-+', '-'
    $Name = $Name -replace '_+', '_'
    $Name = $Name -replace '\s+', ' '
    $Name = $Name -replace '^[-_\s]+|[-_\s]+$', ''
    
    # Truncate if needed
    if ($Name.Length -gt $MaxLength) {
        $Name = $Name.Substring(0, $MaxLength).TrimEnd('-', '_', ' ')
    }
    
    return $Name.Trim()
}

function Sanitize-FolderName {
    param([string]$Name)
    $invalidChars = [IO.Path]::GetInvalidFileNameChars() -join ''
    if ($CleanNames) {
        $Name = Clean-FileName $Name $MaxNameLength
    }
    $Name = $Name -replace "[$([regex]::Escape($invalidChars))]", "_"
    return $Name.Trim()
}

function Get-UniqueFileName {
    param(
        [string]$DestinationFolder,
        [string]$FileName
    )
    
    $baseName = [IO.Path]::GetFileNameWithoutExtension($FileName)
    $extension = [IO.Path]::GetExtension($FileName)
    $fullPath = Join-Path $DestinationFolder $FileName
    $counter = 1
    
    while (Test-Path $fullPath) {
        $newFileName = "${baseName}_${counter}${extension}"
        $fullPath = Join-Path $DestinationFolder $newFileName
        $counter++
    }
    
    return Split-Path $fullPath -Leaf
}

# Main script starts here
if (-not (Test-Path $DestinationPath)) {
    if ($WhatIf) {
        Write-Host "WHATIF: Would create directory: $DestinationPath" -ForegroundColor Yellow
    } else {
        New-Item -ItemType Directory -Path $DestinationPath -Force
        Write-Host "Created destination directory: $DestinationPath" -ForegroundColor Green
    }
}

$totalFiles = 0
$totalProjects = 0
$skippedFiles = 0

$typeFolders = Get-ChildItem -Path $SourcePath -Directory

foreach ($typeFolder in $typeFolders) {
    Write-Host "`nProcessing TYPE folder: $($typeFolder.Name)" -ForegroundColor Cyan
    
    # Create the TYPE folder in PROJECTS
    $typeDestination = Join-Path $DestinationPath $typeFolder.Name
    if (-not (Test-Path $typeDestination)) {
        if ($WhatIf) {
            Write-Host "  WHATIF: Would create TYPE folder: $typeDestination" -ForegroundColor Yellow
        } else {
            New-Item -ItemType Directory -Path $typeDestination -Force
            Write-Host "  Created TYPE folder: $typeDestination" -ForegroundColor Green
        }
    }
    
    $projectFolders = Get-ChildItem -Path $typeFolder.FullName -Directory
    
    foreach ($projectFolder in $projectFolders) {
        Write-Host "  Processing PROJECT: $($projectFolder.Name)" -ForegroundColor White
        
        $sanitizedProjectName = Sanitize-FolderName $projectFolder.Name
        # Fix: Include TYPE folder in the path
        $projectDestination = Join-Path $typeDestination $sanitizedProjectName
        
        $svgFiles = Get-ChildItem -Path $projectFolder.FullName -Filter "*.svg" -Recurse
        
        if ($svgFiles.Count -gt 0) {
            $totalProjects++
            
            if (-not (Test-Path $projectDestination)) {
                if ($WhatIf) {
                    Write-Host "    WHATIF: Would create project folder: $projectDestination" -ForegroundColor Yellow
                } else {
                    New-Item -ItemType Directory -Path $projectDestination -Force
                    Write-Host "    Created project folder: $projectDestination" -ForegroundColor Green
                }
            }
            
            foreach ($svgFile in $svgFiles) {
                $totalFiles++
                
                if ($PreservePath) {
                    $relativePath = $svgFile.FullName.Substring($projectFolder.FullName.Length + 1)
                    $relativeDir = Split-Path $relativePath -Parent
                    $finalDestination = Join-Path $projectDestination $relativeDir
                    
                    if ($relativeDir -and (-not (Test-Path $finalDestination))) {
                        if ($WhatIf) {
                            Write-Host "      WHATIF: Would create subfolder: $finalDestination" -ForegroundColor Yellow
                        } else {
                            New-Item -ItemType Directory -Path $finalDestination -Force
                        }
                    }
                    
                    $fileName = if ($CleanNames) { (Clean-FileName ([IO.Path]::GetFileNameWithoutExtension($svgFile.Name)) $MaxNameLength) + ".svg" } else { $svgFile.Name }
                    $destFile = Join-Path $finalDestination $fileName
                } else {
                    $fileName = if ($CleanNames) { (Clean-FileName ([IO.Path]::GetFileNameWithoutExtension($svgFile.Name)) $MaxNameLength) + ".svg" } else { $svgFile.Name }
                    $uniqueFileName = Get-UniqueFileName $projectDestination $fileName
                    $destFile = Join-Path $projectDestination $uniqueFileName
                }
                
                if ($WhatIf) {
                    Write-Host "      WHATIF: Would copy $($svgFile.Name) to $destFile" -ForegroundColor Yellow
                } else {
                    try {
                        Copy-Item -Path $svgFile.FullName -Destination $destFile -Force
                        Write-Host "      Copied: $($svgFile.Name)" -ForegroundColor Gray
                    } catch {
                        Write-Host "      ERROR copying $($svgFile.Name): $($_.Exception.Message)" -ForegroundColor Red
                        $skippedFiles++
                    }
                }
            }
            
            Write-Host "    Found $($svgFiles.Count) SVG files in this project" -ForegroundColor White
        } else {
            Write-Host "    No SVG files found in this project" -ForegroundColor DarkGray
        }
    }
}

Write-Host "`n" + "="*50 -ForegroundColor Magenta
Write-Host "SUMMARY:" -ForegroundColor Magenta
Write-Host "Projects processed: $totalProjects" -ForegroundColor White
Write-Host "Total SVG files found: $totalFiles" -ForegroundColor White
if ($skippedFiles -gt 0) {
    Write-Host "Files skipped due to errors: $skippedFiles" -ForegroundColor Red
}
if ($WhatIf) {
    Write-Host "This was a test run. Use without -WhatIf to actually copy files." -ForegroundColor Yellow
}
Write-Host "="*50 -ForegroundColor Magenta