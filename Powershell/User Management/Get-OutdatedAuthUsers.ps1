#!ps
# Get-OutdatedAuthUsers.ps1
# Find users using SMS or Phone for MFA - these are being sunsetted Feb 1 2027
# Microsoft announcement: https://learn.microsoft.com/en-us/entra/identity/authentication/concept-sms-voice-retirement

Connect-Graph -Scopes User.Read.All

#$phoneAuthIds = @('b6332ec1-7057-4abe-9331-3d72feddfe41', 'e37fc753-ff3b-4958-9484-eaa9425c82bc','3179e48a-750b-4051-897c-87b9720928f7')

$AuthMethodNames = @{
    '#microsoft.graph.emailAuthenticationMethod'                  = 'Email'
    '#microsoft.graph.externalAuthenticationMethod'                = 'External Identity Provider'
    '#microsoft.graph.fido2AuthenticationMethod'                   = 'FIDO2 Security Key'
    '#microsoft.graph.microsoftAuthenticatorAuthenticationMethod'  = 'Microsoft Authenticator'
    '#microsoft.graph.passwordAuthenticationMethod'                = 'Password'
    '#microsoft.graph.phoneAuthenticationMethod'                   = 'Phone'
    '#microsoft.graph.platformCredentialAuthenticationMethod'      = 'Platform Credential'
    '#microsoft.graph.qrCodePinAuthenticationMethod'              = 'QR Code + PIN'
    '#microsoft.graph.softwareOathAuthenticationMethod'            = 'Software OATH Token'
    '#microsoft.graph.temporaryAccessPassAuthenticationMethod'     = 'Temporary Access Pass'
    '#microsoft.graph.windowsHelloForBusinessAuthenticationMethod' = 'Windows Hello for Business'
}

$phoneAuthUsers = @()
try {
    foreach ($user in Get-MgUser -All) {
        Write-Output "Checking $($user.DisplayName)'s auth methods..."
        $authMethods = Get-MgUserAuthenticationMethod -UserId $user.Id
        $usesPhoneAuth = $false
        $plaintextAuthMethods = ""
        foreach ($authMethod in $authMethods) {
            if ($authMethod.AdditionalProperties["@odata.type"] -eq "#microsoft.graph.phoneAuthenticationMethod") {
                Write-Output "$($user.DisplayName) uses phone/SMS auth!" | Out-Host
                $usesPhoneAuth = $true
            }
            $plaintextAuthMethods = -join ($plaintextAuthMethods, '|', $AuthMethodNames[$authMethod.AdditionalProperties["@odata.type"]])
        }
        if ($usesPhoneAuth) {
            $phoneAuthUsers += @{ Name=$user.DisplayName; PrincipalName=$user.UserPrincipalName; AuthMethods=$plaintextAuthMethods}
        }
    }
}
finally {
    #$phoneAuthUsers | Select-Object @{Name='User'; Expression={$_}} | Export-Csv -Path "./OutdatedAuthUsers.csv" -NoTypeInformation
    $phoneAuthUsers | Export-Csv -Path "./OutdatedAuthUsers.csv" -NoTypeInformation
}
