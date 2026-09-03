# Parameters
$SiteURL = ""
$ListName = ""
$CSVFile = "./output.csv"


# Get the list/library
$List = Get-PnPList -Identity $ListName

# Get the root folder server-relative URL
$RootFolder = Get-PnPProperty -ClientObject $List -Property RootFolder
$LibraryRootUrl = $RootFolder.ServerRelativeUrl.TrimEnd('/')

Write-Host "Library root URL: $LibraryRootUrl"

# Get all files and folders from the library
$global:counter = 0

$AllItems = Get-PnPListItem `
    -List $ListName `
    -PageSize 500 `
    -Fields FileLeafRef, FileRef, FileDirRef, FSObjType `
    -ScriptBlock {
        Param($items)
        $global:counter += $items.Count
        Write-Progress `
            -PercentComplete ($global:counter / $List.ItemCount * 100) `
            -Activity "Getting items from library:" `
            -Status "Processing items $global:counter of $($List.ItemCount)"
    }

Write-Progress -Activity "Completed retrieving items from $ListName" -Completed

# Find items directly under the top level of the library
$TopLevelItems = $AllItems | Where-Object {
    $_.FieldValues.FileDirRef -eq $LibraryRootUrl
}

$FolderStats = @()

foreach ($TopLevelItem in $TopLevelItems) {

    $TopLevelItemName = $TopLevelItem.FieldValues.FileLeafRef
    $TopLevelItemUrl  = $TopLevelItem.FieldValues.FileRef
    $IsFolder         = $TopLevelItem.FileSystemObjectType -eq "Folder"

    if ($IsFolder) {

        # Count all files and folders recursively beneath this top-level folder
        # This excludes the top-level folder itself
        $ChildItems = $AllItems | Where-Object {
            $_.FieldValues.FileRef -like "$TopLevelItemUrl/*"
        }

        $FilesCount = ($ChildItems | Where-Object {
            $_.FileSystemObjectType -eq "File"
        }).Count

        $FoldersCount = ($ChildItems | Where-Object {
            $_.FileSystemObjectType -eq "Folder"
        }).Count

        $TotalItemCount = $FilesCount + $FoldersCount
    }
    else {
        # A top-level file is counted as one item
        $FilesCount = 1
        $FoldersCount = 0
        $TotalItemCount = 1
    }

    $Data = [PSCustomObject][ordered]@{
        Name             = $TopLevelItemName
        Type             = if ($IsFolder) { "Folder" } else { "File" }
        URL              = $TopLevelItemUrl
        FilesCount       = $FilesCount
        SubFolderCount   = $FoldersCount
        TotalItemCount   = $TotalItemCount
    }

    $Data
    $FolderStats += $Data
}

# Export the data to CSV
$FolderStats | Export-Csv -Path $CSVFile -NoTypeInformation

Write-Host "Export completed: $CSVFile"
