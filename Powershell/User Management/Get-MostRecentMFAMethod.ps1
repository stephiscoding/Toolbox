#!ps
# Get-OutdatedAuthUsers.ps1
# Get each user's most recent MFA methods
# Works pretty unreliably. Some accounts it just doesn't pick up any MFA attempts at all.
# Not sure why (I blame Graph), but the script worked well enough at the time I wrote it, so I never bothered investigating.

Connect-Graph -Scopes User.Read.All,Directory.Read.All

$OutdatedAuthUsers = Import-Csv -Path ./OutdatedAuthUsers.csv

$UserAuthMethods = @()
try {
    foreach ($user in $OutdatedAuthUsers) {
        $auditLog = Get-MgBetaAuditLogSignIn -Filter "userPrincipalName eq '$($user.PrincipalName)'" `
        | Select-Object AuthenticationDetails
        Write-Output "Got Audit Log for user $($user.PrincipalName)" | Out-Host
        $MFAauthentications = $auditLog.AuthenticationDetails | Where-Object {$_.AuthenticationMethod -ne "Previously satisfied" -and $_.AuthenticationMethod -ne "Password" -and $_AuthenticationMethod -ne ""} | Select-Object -Property AuthenticationMethod -Unique

        $AuthMethods = ""
        foreach ($MFAauthentication in $MFAauthentications) {
            $AuthMethods = -join ($AuthMethods, '|', $MFAauthentication.AuthenticationMethod)
        }
        $UserAuthMethods += @{UserPrincipalName=$user.PrincipalName; AuthMethods=$AuthMethods}
    }
}
finally {
    $UserAuthMethods | Export-Csv -Path "./UserMFAMethods.csv" -NoTypeInformation
}
