# --- CONFIGURATION SETTINGS ---
$SiteURL = ""
$LibraryName = "" # Change to your target library name
$ExportPath = "./LongSharePointPaths.csv"
$MaxLength = 250 # Adjust this threshold as needed (Max limit is 400)
# ------------------------------

$List = Get-PnPList -Identity $LibraryName
$global:counter = 0

# Fetch all items from the document library
Write-Host "Fetching items from library '$LibraryName'..." -ForegroundColor Cyan
$ListItems = Get-PnPListItem -List $LibraryName -Fields "FileRef", "FileLeafRef", "FileSystemObjectType" -PageSize 2000 `
-ScriptBlock {
    Param($items)
    $global:counter += $items.Count
    Write-Progress `
        -PercentComplete ($global:counter / $List.ItemCount * 100) `
        -Activity "Getting items from library:" `
        -Status "Processing items $global:counter of $($List.ItemCount)"
}

Write-Progress -Activity "Completed retrieving items from $ListName" -Completed

$Results = @()

# Process each item
foreach ($Item in $ListItems) {
    # FileRef contains the full server-relative URL path
    $FullPath = $Item["FileRef"]
    $PathLength = $FullPath.Length

    # Check if the path length exceeds your limit
    if ($PathLength -gt $MaxLength) {
        $Results += [PSCustomObject]@{
            "Name"        = $Item["FileLeafRef"]
            "Path Length" = $PathLength
            "Type"        = $Item["FileSystemObjectType"]
            "RelativeURL" = $FullPath
        }
    }
}

# Export results to CSV if any long paths were found
if ($Results.Count -gt 0) {
    # Ensure destination directory exists
    $TargetDir = Split-Path $ExportPath
    if (!(Test-Path $TargetDir)) { New-Item -ItemType Directory -Path $TargetDir | Out-Null }

    $Results | Export-Csv -Path $ExportPath -NoTypeInformation -Encoding UTF8
    Write-Host "Scan complete! $($Results.Count) items found over $MaxLength characters." -ForegroundColor Green
    Write-Host "Report saved to: $ExportPath" -ForegroundColor Green
} else {
    Write-Host "Scan complete! No file paths exceeded $MaxLength characters." -ForegroundColor Green
}
