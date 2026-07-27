#!ps
# Recreate-Student.ps1
# Checks if an account exists in the Deleted Users section of Entra. Restores it if it exists, creates a new account if it doesn't.
# Once account is set up, sets the password to an admin specified password, and assigns it an A1 for students license if not already assigned.

param (
    [Parameter(Mandatory=$true)][string]$PrincipalName
    # [Parameter(Mandatory=$true)][string]$Password
)

# Connect-Entra -Scopes 'User.ReadWrite.All','Organization.Read.All','LicenseAssignment.Read.All'
Connect-Graph -Scopes User.ReadWrite.All,Organization.Read.All,LicenseAssignment.ReadWrite.All

$passwordInput = Read-Host -Prompt "Enter a password for the user" -MaskInput
$passwordProfile = @{
    ForceChangePasswordNextSignIn = $false
    Password = $passwordInput
}
$A1SKU = Get-MgSubscribedSku -All | Where-Object SkuPartNumber -eq "STANDARDWOFFPACK_STUDENT"

Write-Output "Searching for user..."

# Check if the user already exists
$user = Get-MgUser -UserID $PrincipalName -ErrorAction 'Ignore'
if (($user | Measure-Object).Count -ne 0) {
    Write-Warning "User already exists:"
    Write-Output $user | Out-Host
    $continue = Read-Host -Prompt "Continue setting password and license? (y/n)"
    if ($continue -eq "n") {
        Write-Output "Exiting"
        exit 0
    }
}
else {
    # Check if the user was recently deleted
    $deletedUsers = Get-MgDirectoryDeletedItem -DirectoryObjectId microsoft.graph.user -Property '*'
    $user = $deletedUsers.AdditionalProperties['value'] | Where-Object -Property userPrincipalName -Like "*$PrincipalName"
    if (($user | Measure-Object).Count -ne 0) {
        Write-Warning "User was deleted:"
        Write-Output $user | Out-Host
        $continue = Read-Host -Prompt "Restore user? (y/n)"
        if ($continue -eq "y") {
            Restore-MgDirectoryDeletedItem -DirectoryObjectId $user.id
        }
        else {
            exit 0
        }
        $user = Get-MgUser -UserID $PrincipalName
    }
    # The user does not exist at all - create the user.
    else {
        $continue = Read-Host -Prompt "User $PrincipalName does not exist. Create user? (y/n)"

        if ($continue -eq "y") {
            $displayName = Read-Host -Prompt "Enter a display name for the user"
            $user = New-MgUser `
                -DisplayName $displayName `
                -UserPrincipalName $PrincipalName `
                -PasswordProfile $passwordProfile `
                -mailNickname ($PrincipalName -split "@")[0] `
                -UsageLocation "AU" `
                -accountEnabled `
                # -LicenseAssignment @{SkuId = "314c4481-f395-4525-be8b-2ec4bb1e9d91"} # lol this doesn't work, thanks Microsoft
            Set-MgUserLicense -UserId $user.UserPrincipalName -AddLicenses @{SkuId=$A1SKU.SkuId} -RemoveLicenses @() | Out-Null # so we do this instead

            Write-Output "User created with specified password and A1 License:" | Out-Host
            Write-Output $user | Out-Host
            Write-Host "Don't forget to update the user ID in the management system!" -BackgroundColor DarkMagenta -ForegroundColor White
            exit 0
        }
        else {
            exit 0
        }
    }
}

Write-Output "Setting password for $($user.DisplayName)..."
Update-MgUser -UserId $user.UserPrincipalName -PasswordProfile $passwordProfile | Out-Null

Write-Output "Adding A1 License to $($user.DisplayName)..."
Set-MgUserLicense -UserId $user.UserPrincipalName -AddLicenses @{SkuId=$A1SKU.SkuId} -RemoveLicenses @() | Out-Null

Write-Output "All done! User details:" | Out-Host
Write-Output $user | Out-Host
Write-Host "Don't forget to update the user ID in the management system!" -BackgroundColor DarkMagenta -ForegroundColor White
