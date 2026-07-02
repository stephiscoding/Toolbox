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
    exit 1
}

exit 0
