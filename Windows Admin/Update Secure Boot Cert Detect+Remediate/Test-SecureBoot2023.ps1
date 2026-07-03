$sharePath  = 'C:\Temp'
$hostname   = hostname
$version    = $PSVersionTable.PSVersion.ToString()
$datetime   = Get-Date -F 'yyyyMMddHHmmss'
$filename   = "Test-SecureBoot2023-${hostname}-${version}-${datetime}.txt"
$Transcript = Join-Path -Path $sharePath -ChildPath $filename
Start-Transcript

$ErrorActionPreference = "SilentlyContinue"
try
{
    $secureBootIsEnabled = Confirm-SecureBootUEFI
} catch
{
    # some old firmwares or other issues may cause the above to error out
    exit 0
}

if (-not $secureBootIsEnabled)
{
    # Secure Boot is disabled, no remediation is needed
    exit 0
}


try
{
    $kek = Get-SecureBootUEFI -Name KEK
    $db  = Get-SecureBootUEFI -Name db
} catch
{
    # We can't read the Secure Boot DB, just exit
    exit 0
}

$kekText = [System.Text.Encoding]::Unicode.GetString($kek.Bytes)
$dbText  = [System.Text.Encoding]::Unicode.GetString($db.Bytes)

$HasKEK2023 = $kekText -match "Microsoft Corporation KEK 2K CA 2023"
$HasWindowsUEFICA2023 = $dbText -match "Windows UEFI CA 2023"
$HasMicrosoftUEFICA2023 = $dbText -match "Microsoft UEFI CA 2023"

Write-Debug $kekText
Write-Debug $dbText

if (
    $HasKEK2023 -and
    $HasWindowsUEFICA2023 -and
    $HasMicrosoftUEFICA2023
)
{
    exit 0
} else
{
    # if any of the certificates are not installed, we need to run the remediation component
    Write-Information "Initiating remediation..."
    exit 1
}

exit 0
